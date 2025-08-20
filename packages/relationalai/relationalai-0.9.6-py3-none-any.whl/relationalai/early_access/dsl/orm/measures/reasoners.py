import threading

from relationalai.early_access.dsl.orm.constraints import Mandatory, Unique
from relationalai.early_access.dsl.orm.models import Role, Relationship
from relationalai.early_access.metamodel.util import OrderedSet
from relationalai.early_access.dsl.core import warn

_reasoner_local = threading.local()

def init_reasoner(model):
    _reasoner_local.instance = Reasoner(model)

def get_reasoner():
    try:
        return _reasoner_local.instance
    except AttributeError:
        raise RuntimeError("Reasoner not initialized. Call `init_reasoner(model)` before using it.")

class Reasoner:

    def __init__(self, model):
        self._model = model

        # Map each role's GUID to the relationship it belongs to
        self._role_part_of = {
            role._guid(): relationship
            for relationship in model.relationships()
            for role in (relationship[i] for i in range(relationship._arity()))
        }

        self._role_mandatory = {}
        self._role_spanned_by = {}

        # Process constraints
        for constraint in model._constraints:
            if isinstance(constraint, Mandatory):
                roles = constraint.roles()
                if len(roles) == 1:
                    self._role_mandatory[roles[0]._guid()] = constraint

            elif isinstance(constraint, Unique):
                for r in constraint.roles():
                    self._role_spanned_by[r._guid()] = constraint

        # Filter out external unique constraints
        self._role_spanned_by_internal = {}
        for guid, uc in self._role_spanned_by.items():
            role_guids = {r._part_of()._guid() for r in uc._roles}
            if len(role_guids) == 1:
                self._role_spanned_by_internal[guid] = uc

    # [REKS: TODO] Need to loosen this requirement so that we admit
    #              compatible roles when the player of r1 is a subtype
    #              of that of r2 or vice versa.
    def compatible(self, r1, r2):
        warn(f"Checking compatibility of roles played by {str(r1.player())} and {str(r2.player())} without reasoning about subtypes")
        return r1.player() == r2.player()

    # [REKS: TODO] Need to do the subtype/supertype reasoning required
    #              to properly answer this w/o requring c1 to be equal
    #              to c2
    def least_supertype(self, c1, c2):
        warn(f"Trying to find least supertpe or {str(c1)} and {str(c2)} without reasoning about subtypes")
        return None if str(c1) != str(c2) else c1

    def mandatory(self, role) -> bool:
        return role._guid() in self._role_mandatory

    def model(self): return self._model

    # A role is a "one" role (as opposed to a "many" role) if it is not
    #   spanned by an internal uniqueness constraint
    def one_role(self, role) -> bool:
        return False if role._guid() in self._role_spanned_by_internal else True

    def part_of(self, role) -> Relationship:
        return self._role_part_of[role._guid()]
    
    # [REKS: TODO] Notice that we retain the sibling role ordering from
    #              that of the Relationship, which we currently use to
    #              generate atoms in class MeasureRule and its subclasses.
    #              However, this only works if the measure role of the
    #              Relationship appears in the last position -- which is
    #              almost always the case but is not guaranteed, and we
    #              don't check for it currently
    #
    def role_siblings(self, role) -> OrderedSet[Role]:
        role_guid = role._guid()
        relationship = self.part_of(role)

        return OrderedSet.from_iterable([
            relationship[i]
            for i in range(relationship._arity())
            if relationship[i]._guid() != role_guid
        ])