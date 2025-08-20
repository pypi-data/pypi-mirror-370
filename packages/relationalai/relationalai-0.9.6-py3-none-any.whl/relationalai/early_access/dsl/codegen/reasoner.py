import logging
from typing import Optional

import relationalai.early_access.builder as qb
from relationalai.early_access.dsl.orm.constraints import Unique, Mandatory, RoleValueConstraint, \
    InclusiveSubtypeConstraint, ExclusiveSubtypeConstraint
from relationalai.early_access.dsl.orm.relationships import Role, Relationship
from relationalai.early_access.metamodel.util import OrderedSet


class OntologyReasoner:
    def __init__(self, model):
        self._model = model

        # TODO : populate and use
        self._value_types: OrderedSet[qb.Concept] = OrderedSet()
        self._entity_types: OrderedSet[qb.Concept] = OrderedSet()
        self._exclusive_entity_types: OrderedSet[qb.Concept] = OrderedSet()

        self._concept_identifiers: dict[qb.Concept, OrderedSet[Unique]] = {}
        self._subtype_identifiers: dict[qb.Concept, OrderedSet[Unique]] = {}
        self._constraint_identifies: dict[Unique, qb.Concept] = {}
        self._constructor_roles: OrderedSet[Role] = OrderedSet()
        self._mandatory_roles: OrderedSet[Role] = OrderedSet()

        self._role_value_constraints: OrderedSet[RoleValueConstraint] = OrderedSet()
        self._inclusive_subtype_constraints: OrderedSet[InclusiveSubtypeConstraint] = OrderedSet()
        self._exclusive_subtype_constraints: OrderedSet[ExclusiveSubtypeConstraint] = OrderedSet()

        self._subtype_map: dict[qb.Concept, OrderedSet[qb.Concept]] = {}
        self._supertype_map: dict[qb.Concept, OrderedSet[qb.Concept]] = {}
        self._subtype_closure: dict[qb.Concept, OrderedSet[qb.Concept]] = {}
        self._supertype_closure: dict[qb.Concept, OrderedSet[qb.Concept]] = {}
        self._type_closure: dict[qb.Concept, OrderedSet[qb.Concept]] = {}

        self._analyze()

    #=
    # Constraints: uniqueness and reference schemes.
    #=

    def ref_schemes_of(self, entity_type: qb.Concept, shallow=False) -> OrderedSet[Unique]:
        """
        Returns the reference schemes that are defined for the entity type (plus those inferred from sub- or supertypes).
        """
        own_reference_schemes = self._concept_identifiers.get(entity_type) or OrderedSet()
        if shallow or self.is_exclusive_entity_type(entity_type):
            subtype_reference_schemes = self._subtype_identifiers.get(entity_type) or OrderedSet()
        else:
            subtype_reference_schemes = self.subtype_ref_schemes_of(entity_type)
        return subtype_reference_schemes | own_reference_schemes

    def subtype_unique_ref_scheme_role(self, entity_type: qb.Concept) -> Role:
        """
        Returns the role used to construct the entity type.

        Only valid for simple reference schemes inferred by a subtype.
        """
        ref_schemes = self.ref_schemes_of(entity_type)
        if len(ref_schemes) != 1:
            raise ValueError(f"No unique reference scheme found for {entity_type}")
        ref_scheme = ref_schemes[0]
        return self._extract_unique_role_from_uc(ref_scheme)

    def subtype_ref_schemes_of(self, entity_type: qb.Concept) -> OrderedSet[Unique]:
        """
        Returns the reference schemes that are defined for the entity type and any of its parent types.
        """
        ref_schemes = entity_type._ref_scheme()
        if ref_schemes is None:
            raise ValueError(f"No reference scheme found for {entity_type}")
        identifier_constraints = OrderedSet()
        for relationship in ref_schemes:
            if not isinstance(relationship, Relationship):
                raise ValueError(f"Expected a Relationship, but got {type(relationship)}")
            identifier_constraints.add(self.lookup_identifier_constraint(relationship))
        return identifier_constraints

    def own_ref_scheme_of(self, entity_type: qb.Concept) -> Unique:
        """
        Returns the reference schemes that are defined for the entity type (but not inferred).
        """
        own_ref_schemes = self._concept_identifiers[entity_type]
        if len(own_ref_schemes) != 1:
            raise ValueError(f"Expected exactly one reference scheme for {entity_type}, but got {len(own_ref_schemes)}")
        return own_ref_schemes[0]

    def own_ref_scheme_role(self, entity_type: qb.Concept) -> Role:
        """
        Returns the role used to construct the entity type. Only valid for simple reference schemes.
        """
        ref_scheme = self.own_ref_scheme_of(entity_type)
        return self._extract_unique_role_from_uc(ref_scheme)

    def has_own_ref_scheme(self, entity_type: qb.Concept) -> bool:
        """
        Returns true if the entity type has a reference scheme defined for it.
        """
        return entity_type in self._concept_identifiers

    def has_simple_ref_scheme(self, entity_type: qb.Concept) -> bool:
        ref_schemes = self.ref_schemes_of(entity_type)
        if len(ref_schemes) == 0:
            raise ValueError(f"No reference scheme found for {entity_type}")
        for uc in ref_schemes:
            if len(uc.roles()) > 1:
                return False
        return True

    def has_composite_ref_scheme(self, entity_type: qb.Concept) -> bool:
        return not self.has_simple_ref_scheme(entity_type)

    def is_constructing_role(self, role: Role) -> bool:
        """
        Returns true if the role is a constructing role (i.e., it is used to construct an entity type).
        """
        return role in self._constructor_roles

    def concept_identifiers(self) -> dict[qb.Concept, OrderedSet[Unique]]:
        """
        Returns a mapping of entity types to their reference schemes.
        """
        return self._concept_identifiers

    def is_identifier_relationship(self, relationship: Relationship) -> bool:
        """
        Returns true if the relationship is an identifier relationship (i.e., it is used to construct an entity type).
        """
        if not relationship._binary():
            return False
        for role in relationship._roles():
            if self.is_constructing_role(role):
                return True
        return False

    def lookup_identifier_constraint(self, relationship: Relationship) -> Unique:
        """
        Returns the corresponding identifier constraint for an identifier relationship.
        """
        if not self.is_identifier_relationship(relationship):
            raise ValueError(f"Expected an identifier relationship, but got {relationship}")
        concept_role = None
        constructing_role = None
        for role in relationship._roles():
            if self.is_constructing_role(role):
                concept_role = role.sibling()
                constructing_role = role
            else:
                constructing_role = role.sibling()
                concept_role = role
        assert concept_role is not None and constructing_role is not None, \
            f"Expected both roles to be defined in {relationship}"
        for constraint in self._concept_identifiers[concept_role.player()]:
            if constructing_role in constraint.roles():
                return constraint
        raise ValueError(f"No identifier constraint found for {relationship}")

    def identifies_concept(self, constraint: Unique) -> qb.Concept:
        """
        Returns the concept that is identified by the given uniqueness constraint.
        """
        if constraint not in self._constraint_identifies:
            raise KeyError(f"No concept identified by {constraint}")
        return self._constraint_identifies[constraint]

    def is_composite_concept(self, concept: qb.Concept) -> bool:
        """
        Returns true if the concept is a composite concept (i.e., it has a composite reference scheme).
        """
        ref_schemes = self.ref_schemes_of(concept)
        if len(ref_schemes) == 0:
            return False
        for uc in ref_schemes:
            if len(uc.roles()) > 1:
                return True
        return False

    def is_exclusive_entity_type(self, entity_type: qb.Concept) -> bool:
        """
        Returns true if the entity type is an exclusive entity type).
        """
        return entity_type in self._exclusive_entity_types or self._check_exclusive_supertype(entity_type)

    def _check_exclusive_supertype(self, entity_type: qb.Concept) -> bool:
        """
        Checks if the entity type is an exclusive supertype.
        """
        if self.has_own_ref_scheme(entity_type):
            return False
        subtypes = self._subtype_map.get(entity_type)
        is_exclusive = subtypes is not None
        if is_exclusive:
            self._exclusive_entity_types.add(entity_type)
        return is_exclusive

    def subtype_exclusive_supertype(self, subtype: qb.Concept) -> Optional[qb.Concept]:
        """
        Returns the exclusive supertype of the given subtype if it exists.
        """
        supertypes = self._supertype_map.get(subtype)
        if not supertypes:
            return None
        for supertype in supertypes:
            if self.is_exclusive_entity_type(supertype):
                return supertype
        return None

    @staticmethod
    def _extract_unique_role_from_uc(uc: Unique) -> Role:
        """
        Extracts the unique role from a uniqueness constraint.
        """
        roles = uc.roles()
        if len(roles) != 1:
            raise ValueError(f"Expected exactly one role in uniqueness constraint, but got {len(roles)}")
        return roles[0]

    #=
    # Analysis based on the model.
    #=

    def _analyze(self):
        self._analyze_constraints()
        self._analyze_subtypes()

    #=
    # Look through the constraints, capture the ones that are reference schemes.
    #=

    def _analyze_constraints(self):
        for constraint in self._model.constraints():
            if isinstance(constraint, Unique):
                self._process_uniqueness_constraint(constraint)
            elif isinstance(constraint, Mandatory):
                self._process_mandatory_constraint(constraint)
            elif isinstance(constraint, RoleValueConstraint):
                self._role_value_constraints.add(constraint)
            elif isinstance(constraint, InclusiveSubtypeConstraint):
                self._inclusive_subtype_constraints.add(constraint)
            elif isinstance(constraint, ExclusiveSubtypeConstraint):
                self._exclusive_subtype_constraints.add(constraint)
            else:
                logging.warning(f"Unknown constraint type: {type(constraint)}")

    def _process_uniqueness_constraint(self, constraint: Unique):
        # note: ignoring the ones that are not preferred identifiers for now
        if not constraint.is_preferred_identifier:
            return

        roles = constraint.roles()
        self._constructor_roles.update(roles)  # mark as ctor roles

        if constraint._is_internal():
            # simple ref scheme
            self._process_simple_ref_scheme(constraint)
        else:
            # composite ref scheme
            self._process_composite_ref_scheme(constraint)

    def _process_simple_ref_scheme(self, constraint: Unique):
        role = constraint.roles()[0]
        relation = role._relationship  # actually a DSL Relation
        if relation._arity() != 2:
            raise ValueError(f"Identifier relationship {relation} should have arity 2, but got {relation._arity()}")

        sibling_role = role.sibling()
        assert sibling_role is not None, f"Unable to find the sibling role for {role}"
        constructed_concept = sibling_role.player()
        self._concept_identifiers.setdefault(constructed_concept, OrderedSet()).add(constraint)
        self._constraint_identifies[constraint] = constructed_concept

    def _process_composite_ref_scheme(self, constraint: Unique):
        roles = constraint.roles()
        if len(roles) <= 1:
            raise ValueError(f"External uniqueness constraint should have more than one role, but got {len(roles)}")
        role = roles[0]  # take an arbitrary role to get the constructed concept
        sibling_role = role.sibling()
        assert sibling_role is not None, f"Unable to find the sibling role for {role}"
        constructed_concept = sibling_role.player()
        self._concept_identifiers.setdefault(constructed_concept, OrderedSet()).add(constraint)
        self._constraint_identifies[constraint] = constructed_concept

    def _process_mandatory_constraint(self, constraint: Mandatory):
        role = constraint.roles()[0]
        self._mandatory_roles.add(role)

    #=
    # Look through the subtype hierarchies and capture the preferred IDs (inferring as necessary).
    #=

    def _analyze_subtypes(self):
        self._initialize_type_hierarchy()
        self._infer_subtype_identifiers()
        self._compute_type_closures()

    def _initialize_type_hierarchy(self):
        for child_concept in self._model.entity_types():
            for parent_concept in child_concept._extends:
                self._subtype_map.setdefault(parent_concept, OrderedSet()).add(child_concept)
                self._supertype_map.setdefault(child_concept, OrderedSet()).add(parent_concept)

    def _infer_subtype_identifiers(self):
        (leaf_types, non_leaf_types) = self._partition_type_hierarchy()

        # if a leaf has a ref scheme, then that's what we use; else look it up bottom-up and throw if none found
        memo = set()
        for leaf_type in leaf_types:
            self._find_supertype_identifier_bottom_up(leaf_type, memo, [])

        #=
        # For any intermediate or root nodes that didn't get a ref scheme during the bottom-up lookup, try finding one
        # by doing a top-down lookup (may result in multiple ref schemes from different subtypes).
        #=
        for non_leaf_type in non_leaf_types:
            if non_leaf_type in memo:
                continue
            try:
                self._find_supertype_identifier_bottom_up(non_leaf_type, memo, [])
            except KeyError:
                # mark concept as an exclusive entity type and attempt to find subtype identifiers
                self._exclusive_entity_types.add(non_leaf_type)
                # ignore error, since the top-down approach will throw if none exists either
                self._find_subtype_identifiers_top_down(non_leaf_type, memo, [])

    def _partition_type_hierarchy(self):
        leaf_types = OrderedSet()
        non_leaf_types = OrderedSet()
        non_leaf_types.update(self._subtype_map.keys())
        for entity in self._supertype_map:
            if entity in self._subtype_map:
                non_leaf_types.add(entity)
            else:
                leaf_types.add(entity)
        return leaf_types, non_leaf_types

    def _find_supertype_identifier_bottom_up(self, entity_type: qb.Concept, memo: set[qb.Concept],
                                             lookup_chain: list[qb.Concept]):
        """
        Looks up a ref scheme for an entity type bottom up or throws an error otherwise.

        It's designed to be used on leaf types. If used on intermediate nodes, if they don't have a ref scheme, any
        exception should be swallowed and top-down used to look up a set of possible ref schemes coming from its
        subtypes.
        """
        if entity_type in memo:
            return self._subtype_identifiers.get(entity_type)

        if lookup_chain is None:
            lookup_chain = []
        lookup_chain.append(entity_type)

        ref_schemes = self._concept_identifiers.get(entity_type)
        if ref_schemes is not None:
            self._subtype_identifiers.setdefault(entity_type, OrderedSet()).update(ref_schemes)
            memo.add(entity_type)  # use memoization to reduce lookups
            return ref_schemes
        # Check supertype
        supertypes = self._supertype_map.get(entity_type)
        if supertypes is None:
            raise KeyError(f'No reference scheme found for {entity_type}, in chain {lookup_chain}')
        if len(supertypes) > 1:
            raise NotImplementedError(f'Multiple supertypes are not supported yet (in {entity_type})')
        for supertype in supertypes:
            ref_schemes = self._find_supertype_identifier_bottom_up(supertype, memo, lookup_chain)
            self._subtype_identifiers.setdefault(entity_type, OrderedSet()).update(ref_schemes)
            memo.add(entity_type)  # use memoization to reduce lookups
            return ref_schemes
        raise KeyError(f'No reference scheme found for {entity_type}, in chain {lookup_chain}')

    def _find_subtype_identifiers_top_down(self, entity_type: qb.Concept, memo: set[qb.Concept],
                                           lookup_chain: list[qb.Concept]):
        """
        Looks up a ref scheme for an entity type top-down or throws an error otherwise.

        May result in multiple ref schemes from different subtypes (branches in the subtype tree).
        """
        if entity_type in memo:
            return self._subtype_identifiers.get(entity_type)

        subtypes = self._subtype_map.get(entity_type)
        if subtypes is None:
            raise KeyError(f'No reference scheme found for {entity_type}, in chain {lookup_chain}')

        ref_schemes = OrderedSet()
        for subtype in subtypes:
            subtype_ref_schemes = self._concept_identifiers.get(subtype)
            if subtype_ref_schemes is not None:
                ref_schemes.update(subtype_ref_schemes)
            else:
                lookup_chain.append(subtype)
                subtype_ref_schemes = self._find_subtype_identifiers_top_down(subtype, memo, lookup_chain)
                ref_schemes.update(subtype_ref_schemes)

        self._subtype_identifiers.setdefault(entity_type, OrderedSet()).update(ref_schemes)
        memo.add(entity_type)  # use memoization to reduce lookups
        return ref_schemes

    def _compute_type_closures(self):
        entity_types = self._subtype_map.keys() | self._supertype_map.keys()
        for entity_type in entity_types:
            self._subtype_closure[entity_type] = self._compute_closure(entity_type, self._subtype_map)
            self._supertype_closure[entity_type] = self._compute_closure(entity_type, self._supertype_map)
            self._type_closure[entity_type] = self._subtype_closure[entity_type] | self._supertype_closure[entity_type]

    @staticmethod
    def _compute_closure(entity_type: qb.Concept, closure_map: dict[qb.Concept, OrderedSet[qb.Concept]]) -> OrderedSet[qb.Concept]:
        closure = OrderedSet()
        stack = [entity_type]
        while stack:
            current = stack.pop()
            for related in closure_map.get(current, []):
                if related not in closure:
                    closure.add(related)
                    stack.append(related)
        return closure
