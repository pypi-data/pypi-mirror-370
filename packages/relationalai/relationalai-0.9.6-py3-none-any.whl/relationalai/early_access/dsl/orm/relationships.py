from __future__ import annotations

from typing import Optional, Any, Union

import relationalai.early_access.builder as qb
from relationalai.early_access.builder.builder import RelationshipFieldRef, Field
from relationalai.early_access.dsl.core.utils import generate_stable_uuid
from relationalai.early_access.dsl.orm.utils import generate_rai_way_name


class Relationship(qb.Relationship):

    def __init__(self, model, madlib:Any, short_name:str="", fields:Optional[list[Field]]=None):
        super().__init__(madlib, short_name=short_name, model=model.qb_model(), fields=fields)
        self._dsl_model = model
        self._rel_roles = {field.name: self.__getitem__(field.name) for field in self._fields}
        self._readings[0] = RelationshipReading(self._dsl_model, madlib, self, short_name)

    def __getitem__(self, arg:Union[str, int, qb.Concept]) -> Any:
        rel_field_ref = super().__getitem__(arg)
        field_name = rel_field_ref._field_ref._name
        if hasattr(self, "_rel_roles"):
            if field_name in self._rel_roles:
                return self._rel_roles[field_name]
            else:
                raise ValueError(f"{arg} is undefined for {self._name}")
        return Role._from_field(rel_field_ref)

    def _guid(self):
        return generate_stable_uuid(str(self._id))

    def alt(self, madlib:Any, short_name:str = "", reading:qb.RelationshipReading|None = None) -> qb.RelationshipReading:
        return super().alt(madlib, short_name=short_name,
                           reading=RelationshipReading(self._dsl_model, madlib, self, short_name))

    def _unary(self):
        return self._arity() == 1

    def _binary(self):
        return self._arity() == 2

    def _first(self):
        return self.__getitem__(0)

    def _roles(self):
        return [self._rel_roles[field.name] for field in self._fields]


class RelationshipReading(qb.RelationshipReading):

    def __init__(self, model, madlib:Any, alt_of:Relationship, short_name:str):
        super().__init__(madlib, alt_of, short_name, model=model.qb_model())
        self._dsl_model = model

    def __getitem__(self, arg:Union[str, int, qb.Concept]) -> Any:
        return Role._from_field(super().__getitem__(arg))

    def _guid(self):
        return generate_stable_uuid(str(self._id))

    def _unary(self):
        return self._arity() == 1

    def _binary(self):
        return self._arity() == 2

    def _first(self):
        return self.__getitem__(0)

    def _roles(self):
        return [self._alt_of._rel_roles[field.name] for field in self._fields]

    def rai_way_name(self):
        return generate_rai_way_name(self)


class Role(RelationshipFieldRef):
    _sibling: Optional[Role] = None
    _prefix: Optional[str] = None
    _postfix: Optional[str] = None

    def __init__(self, parent:Any, part_of, pos):
        super().__init__(parent, part_of, pos)

    def _guid(self):
        return generate_stable_uuid(f"{self._field_ix}_{self._part_of()._guid()}")

    def player(self) -> qb.Concept:
        return self._concept

    def sibling(self):
        if self._relationship._arity() == 2 and not self._sibling:
            first_role = self._relationship[0]
            sibling = self._relationship[1] if self._id == first_role._id else first_role
            self._sibling = sibling
        return self._sibling

    def _part_of(self):
        return self._relationship

    def verbalization(self, prefix: Optional[str] = None, postfix: Optional[str] = None):
        self._prefix = prefix
        self._postfix = postfix

    def verbalize(self):
        text_frags = []
        if self._prefix is not None:
            text_frags.append(f"{self._prefix}-")
        text_frags.append(f"{str(self.player())}")
        if self._postfix is not None:
            text_frags.append(f"-{self._postfix}")
        return " ".join(text_frags)

    @property
    def postfix(self) -> Optional[str]:
        return self._postfix

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    @staticmethod
    def _from_field(field:RelationshipFieldRef):
        return Role(field._parent, field._relationship, field._field_ix)

    def __hash__(self):
        return hash(f"Role({self._guid()})")

    def __eq__(self, other):
        if not isinstance(other, Role):
            return False
        return self._guid() == other._guid() and self._part_of() == other._part_of()
