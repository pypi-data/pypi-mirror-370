from __future__ import annotations

from collections import OrderedDict
from typing import Optional, Any, Sequence, Union, TypeVar

import relationalai.early_access.builder as qb
from relationalai import Config
from relationalai.early_access.dsl.bindings.common import Binding
from relationalai.early_access.dsl.bindings.csv import CsvTable
from relationalai.early_access.dsl.bindings.snowflake import SnowflakeTable
from relationalai.early_access.dsl.codegen.weaver import Weaver
from relationalai.early_access.dsl.core.utils import generate_stable_uuid, to_pascal_case
from relationalai.early_access.dsl.orm.constraints import Unique, Mandatory, RoleValueConstraint, Range, \
    ExclusiveSubtypeConstraint, InclusiveSubtypeConstraint, InclusiveRoleConstraint, ExclusiveRoleConstraint, \
    RingConstraint, ValueComparisonConstraint, RoleSubsetConstraint, EqualityConstraint, FrequencyConstraint, \
    CardinalityConstraint, RoleCardinalityConstraint
from relationalai.early_access.dsl.orm.relationships import Relationship, Role, RelationshipReading
from relationalai.early_access.dsl.orm.types import Concept
from relationalai.early_access.dsl.snow.api import Executor
from relationalai.early_access.metamodel.util import OrderedSet

T = TypeVar('T', int, float, str)

class Model:
    def __init__(
            self,
            name: str,
            is_primary: bool = True,
            dry_run: bool = False,
            use_lqp: bool = False,
            use_sql: bool = False,
            wide_outputs: bool = False,
            config: Optional[Config] = None
    ):
        self.name = name
        self._qb_model = qb.Model(name, dry_run=dry_run, strict=True, config=config, use_lqp=use_lqp, use_sql=use_sql, wide_outputs=wide_outputs)
        self.is_primary = is_primary
        self._constraints = OrderedSet()
        self._entity_to_id_relationship = OrderedDict()
        self._bindable_tables = OrderedDict()
        self._relationship_iuc: dict[qb.Relationship, list[Unique]] = {}
        self._bindings = []
        self._executor = None
        self._weaver = None
        self._queries = OrderedSet()
        self.Enum = self._qb_model.Enum

    def guid(self):
        return generate_stable_uuid(self.name)

    def Concept(self, name: str, extends: list[Any] = [], identify_by:dict[str, Any]={}) -> Concept:
        name = to_pascal_case(name)
        return Concept(self, name, extends, identify_by)

    def qb_model(self):
        return self._qb_model

    def Relationship(self, reading: Any, short_name:str="") -> qb.Relationship:
        """
        Create a new relationship with the given reading.
        """
        return Relationship(self, reading, short_name=short_name)

    def constraint(self, constraint):
        # Generic constraint addition with validation
        self._constraints.add(constraint)
        constraint._desugar()

    def unique(self, *roles):
        uc = Unique(*roles)
        self.constraint(uc)
        first_part_of = roles[0]._part_of()
        if isinstance(first_part_of, RelationshipReading):
            relationship = first_part_of._alt_of
        else:
            relationship = first_part_of
        # check if UC is internal
        if all(role._part_of()._id == first_part_of._id for role in roles):
            field_refs = set(r._field_ref for r in roles)
            internal_ucs = self._relationship_iuc.get(relationship, [])
            # create sets of ref fields declared for the relationship
            iuc_ref_sets = [set(r._field_ref for r in uc.roles()) for uc in internal_ucs]
            for reading in relationship._readings:
                refs_except_last = set(reading._field_refs[:-1])
                # when internal UC declared for all the roles except the last one in the RelationshipReading mark RelationshipReading as `is_many=False`
                if field_refs == refs_except_last:
                    reading._is_many = False
                elif not reading._is_many:
                    # check that a reading already has an internal uc with the roles except the last one
                    # if not then mark reading as `is_many=True`
                    if all(refs != refs_except_last for refs in iuc_ref_sets):
                        reading._is_many = True
            internal_ucs.append(uc)
            self._relationship_iuc[relationship] = internal_ucs  # todo: this logic should be part of reactive reasoner

    def mandatory(self, role):
        self.constraint(Mandatory(role))

    def inclusive_roles(self, *roles):
        self.constraint(InclusiveRoleConstraint(*roles))

    def exclusive_roles(self, *role_sequences):
        self.constraint(ExclusiveRoleConstraint(*role_sequences))

    def ring(self, constraint_types, *roles):
        self.constraint(RingConstraint(constraint_types, *roles))

    def value_comparison(self, constraint_type, *roles):
        self.constraint(ValueComparisonConstraint(constraint_type, *roles))

    def role_subset(self, *role_sequences):
        self.constraint(RoleSubsetConstraint(*role_sequences))

    def equality(self, *role_sequences):
        self.constraint(EqualityConstraint(*role_sequences))

    def frequency(self, frequency, *role_sequences):
        self.constraint(FrequencyConstraint(frequency, *role_sequences))
    def cardinality(self, concept: Concept, values: Sequence[Union[int, Range[int]]]):
        self.constraint(CardinalityConstraint(concept, values))

    def role_cardinality(self, role: Role, values: Sequence[Union[int, Range[int]]]):
        self.constraint(RoleCardinalityConstraint(role, values))

    def role_value_constraint(self, role: Role, values: Sequence[Union[T, Range[T]]]):
        first_type = values[0]._type() if isinstance(values[0], Range) else type(values[0])
        for v in values[1:]:
            t = v._type() if isinstance(v, Range) else type(v)
            if t != first_type:
                raise Exception("Values for role value constraint must have the same type.")
        if role.player()._is_primitive() or role.player()._is_value_type():
            self.constraint(RoleValueConstraint(role, values))
        else:
            raise Exception("A role value constraint can only be applied to roles played by value types")

    def exclusive_subtype_constraint(self, *concepts:Concept):
        self.constraint(ExclusiveSubtypeConstraint(*concepts))

    def inclusive_subtype_constraint(self, *concepts:Concept):
        self.constraint(InclusiveSubtypeConstraint(*concepts))

    def _add_concept(self, concept: Concept) -> Concept:
        self._validate_type_name(concept._name)
        if concept._name not in self.qb_model().concepts:
            self.qb_model().concepts[concept._name] = [concept]
        return concept

    def _ref_scheme_constraints(self, *relations:Relationship):
        if len(relations) == 1:
            # binary case, internal UC
            role = relations[0][1]
            self._internal_preferred_uc(role)
        else:
            roles = [rel[1] for rel in relations]
            self._composite_preferred_uc(*roles)

    def _internal_preferred_uc(self, role):
        rel = role._part_of()
        if rel._arity() != 2:
            raise Exception("The relationship should be binary to apply preferred identifier constraint")
        # mark the role as preferred identifier
        self.constraint(Unique(role, is_preferred_identifier=True))
        # mark the sibling role as mandatory and unique
        sibling = role.sibling()
        self.mandatory(sibling)
        self.unique(sibling)

    def _composite_preferred_uc(self, *roles):
        for role in roles:
            sibling = role.sibling()
            if not sibling:
                raise Exception("Composite preferred identifier constraint should be applied on binary relationships")
            self.mandatory(sibling)
            self.unique(sibling)
        self.constraint(Unique(*roles, is_preferred_identifier=True))

    def lookup_concept(self, name) -> Optional[qb.Concept]:
        name = to_pascal_case(name)
        if name in self._qb_model.concepts:
            return self._qb_model.concepts[name][0]
        return None

    def constraints(self):
        """Getter for the _constraints property"""
        return self._constraints

    def queries(self):
        return self._queries

    def concepts(self):
        c = list()
        for concepts in self._qb_model.concepts.values():
            c.append(concepts[0])
        return c

    def concepts_map(self):
        d = dict()
        for k, v in self._qb_model.concepts.items():
            d[k] = v[0]
        return d

    def enums(self):
        return list(self._qb_model.enums.values())

    def enums_map(self):
        return self._qb_model.enums

    def value_types(self):
        return list(filter(lambda c: c._is_primitive(), self.concepts()))

    def value_types_map(self):
        return dict(filter(lambda item: item[1]._is_primitive(), self.concepts_map().items()))

    def entity_types(self):
        return list(filter(lambda c: not c._is_primitive(), self.concepts()))

    def entity_types_map(self):
        return dict(filter(lambda item: not item[1]._is_primitive(), self.concepts_map().items()))

    def relationships(self):
        return self._qb_model.relationships

    def bindable_tables(self):
        return self._bindable_tables

    def api(self):
        self._executor = self._executor or Executor(self._qb_model._config)
        return self._executor

    def table(self, name: str) -> SnowflakeTable:
        table = SnowflakeTable(name, self)
        self._bindable_tables[name] = table
        return table

    def csv_table(self, name: str, schema: dict[str, qb.Concept]) -> CsvTable:
        table = CsvTable(name, schema, self)
        self._bindable_tables[name] = table
        return table

    def binding(self, binding: Binding):
        self._bindings.append(binding)

    def generate_model_rules(self, config: Optional[dict]=None):
        if self._weaver is None:
            self._weaver = Weaver(self, config)
        else:
            raise Exception("Model rules have already been generated.")
        self._weaver.generate()

    def delete(self):
        self.api().provider().delete_model(self.name)

    def _validate_type_name(self, name):
        if name in self._qb_model.concepts:
            raise Exception(
                f"The name '{name}' is used to declare a Concept.")
