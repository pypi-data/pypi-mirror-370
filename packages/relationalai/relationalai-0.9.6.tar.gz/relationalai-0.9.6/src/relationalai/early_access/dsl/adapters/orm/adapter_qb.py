import warnings
from collections import defaultdict
from typing import Optional
from relationalai import Config
from relationalai.early_access.dsl.adapters.orm.model import ExclusiveInclusiveSubtypeFact, ExclusiveSubtypeFact, \
    ORMRingType, ORMValueComparisonOperator, ORMRange
from relationalai.early_access.dsl.adapters.orm.parser import ORMParser
from relationalai.early_access.dsl.core.utils import to_pascal_case
from relationalai.early_access.dsl.orm.constraints import RingType, ValueComparisonType, Range
from relationalai.early_access.dsl.orm.models import Model
from relationalai.early_access.builder import Concept, Integer, String, DateTime, Decimal, Date, Float
from relationalai.early_access.metamodel.util import NameCache
from datetime import date, datetime
from decimal import Decimal as PyDecimal

class ORMAdapterQB:
    _datatype_mapping = {
        "SignedIntegerNumericDataType": Integer,
        "SignedLargeIntegerNumericDataType": Integer,
        "UnsignedIntegerNumericDataType": Integer,
        "UnsignedTinyIntegerNumericDataType": Integer,
        "UnsignedSmallIntegerNumericDataType": Integer,
        "UnsignedLargeIntegerNumericDataType": Integer,
        "AutoCounterNumericDataType": Integer,
        "FloatingPointNumericDataType": Float,
        "SinglePrecisionFloatingPointNumericDataType": Float,
        "DoublePrecisionFloatingPointNumericDataType": Float,
        "DecimalNumericDataType": Decimal,
        "MoneyNumericDataType": Decimal,
        "FixedLengthTextDataType": String,
        "VariableLengthTextDataType": String,
        "LargeLengthTextDataType": String,
        "DateTemporalDataType": Date,
        "DateAndTimeTemporalDataType": DateTime,
        "AutoTimestampTemporalDataType": DateTime,
        "TimeTemporalDataType": DateTime,
    }

    _builtin_concepts_to_python_types = {
        Concept.builtins["Int"]: int,
        Concept.builtins["Float"]: float,
        Concept.builtins["String"]: str,
        Concept.builtins["Bool"]: bool,
        Concept.builtins["Date"]: date,
        Concept.builtins["DateTime"]: datetime,
        Concept.builtins["Decimal128"]: PyDecimal
    }

    _ring_type_mapping = {
        ORMRingType.IRREFLEXIVE: RingType.IRREFLEXIVE,
        ORMRingType.ANTISYMMETRIC: RingType.ANTISYMMETRIC,
        ORMRingType.ASYMMETRIC: RingType.ASYMMETRIC,
        ORMRingType.INTRANSITIVE: RingType.INTRANSITIVE,
        ORMRingType.STRONGLY_INTRANSITIVE: RingType.STRONGLY_INTRANSITIVE,
        ORMRingType.ACYCLIC: RingType.ACYCLIC,
        ORMRingType.PURELY_REFLEXIVE: RingType.PURELY_REFLEXIVE,
        ORMRingType.REFLEXIVE: RingType.REFLEXIVE,
        ORMRingType.SYMMETRIC: RingType.SYMMETRIC,
        ORMRingType.TRANSITIVE: RingType.TRANSITIVE
    }

    _value_comparison_type_mapping = {
        ORMValueComparisonOperator.GREATER_THAN_OR_EQUAL: ValueComparisonType.GREATER_THAN_OR_EQUAL,
        ORMValueComparisonOperator.LESS_THAN_OR_EQUAL: ValueComparisonType.LESS_THAN_OR_EQUAL,
        ORMValueComparisonOperator.GREATER_THAN: ValueComparisonType.GREATER_THAN,
        ORMValueComparisonOperator.LESS_THAN: ValueComparisonType.LESS_THAN,
        ORMValueComparisonOperator.NOT_EQUAL: ValueComparisonType.NOT_EQUAL,
        ORMValueComparisonOperator.EQUAL: ValueComparisonType.EQUAL
    }

    def __init__(self, orm_file_path: str, model_name: Optional[str] = None, config: Optional[Config] = None):
        self._parser = ORMParser(orm_file_path)
        self._relationship_role_value_constraints = defaultdict()
        self._relationships = {}
        self.name_cache = NameCache()
        self.model = self._orm_to_model(model_name, config)

    def _orm_to_model(self, model_name, config):
        model = Model(model_name, config=config) if model_name else Model(self._parser.model_name(), config=config)

        self._add_value_types(model)
        self._add_entity_types(model)
        self._add_subtype_relationships(model)
        self._add_relationships(model)
        self._add_external_identifying_relationships(model)
        self._add_role_value_constraints(model)
        self._add_inclusive_role_constraints(model)
        self._add_exclusive_role_constraints(model)
        self._add_ring_constraints(model)
        self._add_value_comparison_constraints(model)
        self._add_role_subset_constraints(model)
        self._add_equality_constraints(model)
        self._add_frequency_constraints(model)
        return model

    def _add_value_types(self, model):
        enum_to_values = defaultdict(list)
        for rvc in self._parser.role_value_constraints().values():
            if self._is_value_type_an_enum(rvc.role.id):
                enum_to_values[rvc.role.player].extend(rvc.values)

        cardinality_constraints = self._parser.objects_type_to_cardinality_constraints()
        for vt in self._parser.value_types().values():
            if vt.id in enum_to_values:
                concept = model.Enum(to_pascal_case(vt.name), enum_to_values[vt.id])
            else:
                concept = model.Concept(vt.name, extends=[self._datatype_mapping.get(vt.data_type, String)])
            if vt.name in cardinality_constraints:
                model.cardinality(concept, self._build_constraint_ranges(cardinality_constraints[vt.name]))

    def _add_entity_types(self, model):
        extended_concepts = [y.subtype_name for x in self._parser.subtype_facts().values() for y in x]
        cardinality_constraints = self._parser.objects_type_to_cardinality_constraints()
        for et in self._parser.entity_types().values():
            if et.name not in extended_concepts:
                concept = model.Concept(et.name)
                if et.name in cardinality_constraints:
                    model.cardinality(concept, self._build_constraint_ranges(cardinality_constraints[et.name]))

        subtype_facts = self._parser.sorted_subtype_facts()
        for st_fact in subtype_facts:
            parent = st_fact.supertype_name
            parent_entity = model.lookup_concept(parent)
            if parent_entity is None:
                parent_entity = model.Concept(parent)
                if parent in cardinality_constraints:
                    model.cardinality(parent_entity, self._build_constraint_ranges(cardinality_constraints[parent]))
            child = st_fact.subtype_name
            child_entity = model.Concept(child, extends=[parent_entity])
            if child in cardinality_constraints:
                model.cardinality(child_entity, self._build_constraint_ranges(cardinality_constraints[child]))

    def _add_subtype_relationships(self, model):
        for parent, children in self._parser.subtype_facts().items():
            exclusives = []
            exclusives_and_inclusives = []
            for child in children:
                sub = model.lookup_concept(child.subtype_name)
                if isinstance(child, ExclusiveInclusiveSubtypeFact):
                    exclusives_and_inclusives.append(sub)
                elif isinstance(child, ExclusiveSubtypeFact):
                    exclusives.append(sub)

            if len(exclusives_and_inclusives) > 0:
                model.exclusive_subtype_constraint(*exclusives_and_inclusives)
                model.inclusive_subtype_constraint(*exclusives_and_inclusives)
            if len(exclusives) > 0:
                model.exclusive_subtype_constraint(*exclusives)

    def _add_relationships(self, model):
        object_types = self._parser.object_types()
        unique_roles = self._parser.unique_roles()
        mandatory_roles = self._parser.mandatory_roles()
        role_value_constraints = self._parser.role_value_constraints()
        role_cardinality_constraints = self._parser.role_cardinality_constraints()
        fact_type_to_internal_ucs = self._parser.fact_type_to_internal_ucs()
        fact_type_to_complex_ucs = self._parser.fact_type_to_complex_ucs()
        fact_type_to_roles = self._parser.fact_type_to_roles()
        for fact_type, reading_orders in self._parser.fact_type_readings().items():

            # Adding the main reading
            rdo = reading_orders[0]
            player = object_types[rdo.roles[0].role.player].name
            player_entity = model.lookup_concept(player)
            reading = self._build_reading(model, rdo)
            relationship = model.Relationship(reading)
            self._set_role_verbalization(relationship, rdo)
            short_name = self._pick_short_name(model, player_entity, fact_type, relationship._readings[0])
            cached_name = self.name_cache.get_name(relationship._readings[0], f"{player_entity._name}.{short_name}")
            short_name = cached_name.split(".")[1]
            setattr(player_entity, short_name, relationship)
            self._relationships[fact_type] = relationship


            # Marking unique and mandatory roles
            role_idx_to_player = []
            for ro in rdo.roles:
                role_id = ro.role.id
                role_idx_to_player.append(role_id)
                role_index = role_idx_to_player.index(role_id)
                role = relationship[role_index]
                if role_id in unique_roles:
                    model.unique(role)
                if role_id in mandatory_roles:
                    model.mandatory(role)
                if role_id in role_value_constraints.keys():
                    self._relationship_role_value_constraints[role] = role_value_constraints[role_id].values
                if role_id in role_cardinality_constraints.keys():
                    model.role_cardinality(role, self._build_constraint_ranges(role_cardinality_constraints[role_id]))


            # Adding alternative readings
            self._validate_role_verbalization(reading_orders)

            if len(reading_orders) > 1:
                for rdo in reading_orders[1:]:
                    other_player = object_types[rdo.roles[0].role.player].name
                    other_player_entity = model.lookup_concept(other_player)
                    alt_reading = self._build_reading(model, rdo)
                    alt_reading_obj = relationship.alt(alt_reading)
                    short_name = self._pick_short_name(model, other_player_entity, fact_type, alt_reading_obj)
                    cached_name = self.name_cache.get_name(alt_reading_obj, f"{other_player_entity._name}.{short_name}")
                    short_name = cached_name.split(".")[1]
                    setattr(other_player_entity, short_name, alt_reading_obj)

            # Marking identifying relationships
            if fact_type in fact_type_to_internal_ucs:
                for uc in fact_type_to_internal_ucs[fact_type]:
                    if uc.identifies:
                        player_entity.identify_by(relationship)

            # Adding constraint spanning over multiple roles
            if fact_type in fact_type_to_complex_ucs:
                for uc in fact_type_to_complex_ucs[fact_type]:
                    uc_roles = []
                    for role in fact_type_to_roles[fact_type]:

                        if role.id in uc.roles:
                            p = role.id
                            rl = role_idx_to_player.index(p)
                            uc_roles.append(self._relationships[fact_type][rl])
                    model.unique(*uc_roles)

    def _add_external_identifying_relationships(self, model):
        roles = self._parser.roles()
        object_types = self._parser.object_types()
        for uc in self._parser.external_uniqueness_constraints().values():
            # Identifying external UCs
            if uc.identifies:
                entity = model.lookup_concept(object_types[uc.identifies].name)
                identifying_rel = []
                for ro in uc.roles:
                    relationship = self._relationships[roles[ro].relationship_name]
                    # TODO: this will change when we can use readings or roles with identify_by
                    if relationship._roles()[0]._concept._name != entity._name:
                        raise ValueError(f"The concept {entity._name} must be the first player in all its identifying relationships.")
                    identifying_rel.append(relationship)
                entity.identify_by(*identifying_rel)
            # Non identifying external UCs
            else:
                role_list = []
                for ro in uc.roles:
                    relationship = self._relationships[roles[ro].relationship_name]
                    role = relationship._rel_roles[object_types[roles[ro].player].name.lower()]
                    role_list.append(role)
                model.unique(*role_list)

    def _add_inclusive_role_constraints(self, model):
        for rc in self._parser.inclusive_role_constraints():
            constraint_roles = self._get_roles_from_orm_constraint(model, rc)
            model.inclusive_roles(*constraint_roles)

    def _add_exclusive_role_constraints(self, model):
        for rc in self._parser.exclusive_role_constraints():
            constraint_roles = self._get_roles_from_orm_constraint(model, rc)
            model.exclusive_roles(*constraint_roles)

    def _add_ring_constraints(self, model):
        for rc in self._parser.ring_constraints().values():
            constraint_roles = self._get_roles_from_orm_constraint(model, rc)
            constraint_types = [self._ring_type_mapping.get(rt) for rt in rc.ring_types]
            model.ring(constraint_types, *constraint_roles)

    def _add_value_comparison_constraints(self, model):
        for vcc in self._parser.value_comparison_constraints().values():
            constraint_roles = self._get_roles_from_orm_constraint(model, vcc)
            constraint_type = self._value_comparison_type_mapping.get(vcc.operator)
            model.value_comparison(constraint_type, *constraint_roles)

    def _add_role_subset_constraints(self, model):
        for rsc in self._parser.role_subset_constraints().values():
            constraint_roles = self._get_roles_from_orm_constraint(model, rsc)
            model.role_subset(*constraint_roles)

    def _add_equality_constraints(self, model):
        for ec in self._parser.equality_constraints().values():
            constraint_roles = self._get_roles_from_orm_constraint(model, ec)
            model.equality(*constraint_roles)

    def _add_frequency_constraints(self, model):
        for fc in self._parser.frequency_constraints().values():
            constraint_roles = self._get_roles_from_orm_constraint(model, fc)
            constraint_frequency = (fc.min_frequency, fc.max_frequency)
            model.frequency(constraint_frequency, *constraint_roles)

    def _add_role_value_constraints(self, model):
        for role, values in self._relationship_role_value_constraints.items():
            extends = role._concept._extends[0]
            if extends._name == "Enum":
                model.role_value_constraint(role, values)
            else:
                tp = self._builtin_concepts_to_python_types.get(extends)
                if tp:
                    constraint_values = []
                    for value in values:
                        if isinstance(value, ORMRange):
                            constraint_values.append(self._build_constraint_range(value, tp))
                        else:
                            constraint_values.append(tp(value))
                    model.role_value_constraint(role, constraint_values)
                else:
                    raise ValueError(f"Unsupported type for role value constraint: {extends._name}.")

    def _build_reading(self, model, reading_order):
        object_types = self._parser.object_types()
        rel_args = []
        if reading_order.front_text is not None:
            rel_args.append(f"{reading_order.front_text} ")
        for rdo_role in reading_order.roles:
            p = model.lookup_concept(object_types[rdo_role.role.player].name)
            rel_args.append(f"{{{p}}}") if rdo_role.role.name == "" else rel_args.append(f"{{{rdo_role.role.name}:{p}}}")
            if rdo_role.text is not None:
                rel_args.append(f" {rdo_role.text} ")
        return ''.join(rel_args).strip()

    def _rename_to_ref_mode(self, model, first_player_entity, fact_type):
        identifier_fact_type_to_entity_type = self._parser.identifier_fact_type_to_entity_type()
        entity_type = identifier_fact_type_to_entity_type.get(fact_type)
        if entity_type:
            player = model.lookup_concept(entity_type.name)
            if first_player_entity._id == player._id:
                return entity_type.ref_mode
        return None

    def _pick_short_name(self, model, player_entity, fact_type, reading):
        ref_mode = self._rename_to_ref_mode(model, player_entity, fact_type)
        if ref_mode is not None:
            rel_name = ref_mode.lower()
        else:
            rel_name = reading.rai_way_name()
        return rel_name

    def _role_id_to_role_object(self, model, role_obj):
        player_entity = model.lookup_concept(self._parser.object_types()[role_obj.player].name)
        rel = self._relationships[role_obj.relationship_name]
        if role_obj.name == "":
            idx = rel._field_names.index(player_entity._name.lower())
        else:
            idx = rel._field_names.index(role_obj.name)
        return rel[idx]

    def _get_roles_from_orm_constraint(self, model, orm_constraint):
        roles = self._parser.roles()
        # Role sequences
        if all(isinstance(item, list) for item in orm_constraint.roles):
            return [[self._role_id_to_role_object(model, roles[ro]) for ro in ro_list] for ro_list in orm_constraint.roles]
        # Role list
        else:
            return [self._role_id_to_role_object(model, roles[ro]) for ro in orm_constraint.roles]

    # A Value type that plays a given role is an Enum when there is a role value constraint containing only string
    # values declared on this ValueType, and it does not play a role in any other relationship
    def _is_value_type_an_enum(self, role_id):
        role_value_constraint = self._parser.role_value_constraints().get(role_id)
        return (
                role_value_constraint
                and role_value_constraint.values
                and all(isinstance(v, str) for v in role_value_constraint.values)
                and self._count_relationships_for_player(role_value_constraint.role.player) == 1
        )

    def _count_relationships_for_player(self, player_id):
        count = 0
        for v in self._parser._role_to_player.values():
            if v == player_id:
                count += 1
        return count

    @staticmethod
    def _build_constraint_range(range: ORMRange, tp: type):
        if range.range_from == range.range_to:
            return tp(range.range_from)
        return Range.between(tp(range.range_from), tp(range.range_to))

    @staticmethod
    def _build_constraint_ranges(constraint):
        constraint_ranges = []
        for rg in constraint.ranges:
            constraint_ranges.append(ORMAdapterQB._build_constraint_range(rg, int))
        return constraint_ranges

    @staticmethod
    def _set_role_verbalization(relationship, rdo):
        for idx, ro in enumerate(rdo.roles):
            qb_role = relationship._roles()[idx]
            text_chunks = [None, None]
            if ro.prefix:
                text_chunks[0] = ro.prefix
            if ro.postfix:
                text_chunks[1] = ro.postfix
            if text_chunks[0] or text_chunks[1]:
                qb_role.verbalization(*text_chunks)

    @staticmethod
    def _validate_role_verbalization(reading_orders):
        if len(reading_orders) > 1:
            relationship = reading_orders[0].roles[0].role.relationship_name
            for ro in reading_orders[0].roles:
                prefix = ro.prefix
                postfix = ro.postfix
                player = ro.role.player
                #  A role player must have the same prefix in all readings
                if not all(alt_ro.prefix == prefix for rdo in reading_orders[1:] for alt_ro in rdo.roles if alt_ro.role.player == player):
                    warnings.warn(f"Ignoring incompatible prefix in alternative readings of {relationship}.")
                #  A role player must have the same postfix in all readings
                if not all(alt_ro.postfix == postfix for rdo in reading_orders[1:] for alt_ro in rdo.roles if alt_ro.role.player == player):
                    warnings.warn(f"Ignoring incompatible postfix in alternative readings of {relationship}")
