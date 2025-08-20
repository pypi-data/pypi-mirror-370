from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum, EnumMeta
import re
from typing import Any, Sequence as PySequence, Type, cast
import itertools
import rich

from pandas import DataFrame
import numpy as np
import pandas as pd
from more_itertools import peekable

from relationalai import debugging, errors
from relationalai.environments.base import find_external_frame
from relationalai.clients.config import Config
from relationalai.clients.result_helpers import Int128Dtype
from relationalai.early_access.metamodel import factory as f, helpers, ir, builtins, types
from relationalai.early_access.metamodel.util import NameCache, OrderedSet, ordered_set
from relationalai.early_access.rel.executor import RelExecutor
from relationalai.early_access.lqp.executor import LQPExecutor
from relationalai.early_access.devmode.executor.snowflake import SnowflakeExecutor
from relationalai.environments import runtime_env
from collections import Counter

from datetime import date, datetime
from decimal import Decimal as PyDecimal

#--------------------------------------------------
# Globals
#--------------------------------------------------

_global_id = peekable(itertools.count(0))

# Single context variable with default values
_overrides = ContextVar("overrides", default = {})
def overrides(key: str, default: bool | str):
    return _overrides.get().get(key, default)

# Flag that users set in the config or directly on the model, but that can still be
# overridden globally. Precedence is overrides > model argument > config.
def overridable_flag(key: str, config: Config, user_pref: bool | None, default: bool):
    if user_pref is not None:
        preferred = cast(bool, user_pref)
    else:
        preferred = cast(bool, config.get(key, default))
    return overrides(key, preferred)

@contextmanager
def with_overrides(**kwargs):
    token = _overrides.set({**_overrides.get(), **kwargs})
    try:
        yield
    finally:
        _overrides.reset(token)

#--------------------------------------------------
# Root tracking
#--------------------------------------------------

_track_default = True
_track_roots = ContextVar('track_roots', default=_track_default)
_global_roots = ordered_set()

def _add_root(root):
    if _track_roots.get():
        _global_roots.add(root)

def _remove_roots(items: PySequence[Producer|Fragment]):
    for item in items:
        if hasattr(item, "__hash__") and item.__hash__ and item in _global_roots:
            _global_roots.remove(item)

# decorator
def roots(enabled=_track_default):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = _track_roots.set(enabled)
            try:
                return func(*args, **kwargs)
            finally:
                _track_roots.reset(token)
        return wrapper
    return decorator

# with root_tracking(enabled=False): ...
@contextmanager
def root_tracking(enabled=_track_default):
    token = _track_roots.set(enabled)
    try:
        yield
    finally:
        _track_roots.reset(token)

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def unwrap_list(item:Any) -> Any:
    if isinstance(item, (list, tuple)) and len(item) == 1:
        return item[0]
    elif isinstance(item, (list, tuple)) and len(item) > 1:
        raise ValueError(f"Expected a single item, got {len(item)}")
    return item

def flatten(items:PySequence[Any], flatten_tuples=False) -> list[Any]:
    flat = []
    for item in items:
        if isinstance(item, (list, tuple)) and (flatten_tuples or not isinstance(item, TupleArg)):
            flat.extend(flatten(item, flatten_tuples=flatten_tuples))
        else:
            flat.append(item)
    return flat

def find_subjects(items: PySequence[Producer]) -> set[Concept|Ref]:
    subjects = set()
    for item in items:
        if isinstance(item, Concept):
            subjects.add(item)
        elif isinstance(item, ConceptExpression):
            subjects.add(item._op)
        elif isinstance(item, Expression):
            subjects.update(find_subjects(item._params))
        elif isinstance(item, Ref):
            subjects.add(item)
        elif isinstance(item, Relationship) and item._parent:
            subjects.update(find_subjects([item._parent]))
    return subjects

def to_type(item: Any) -> Concept|None:
    if isinstance(item, Concept):
        return item
    elif isinstance(item, (Ref, Alias)):
        return to_type(item._thing)
    elif isinstance(item, ConceptExpression):
        return to_type(item._op)
    elif isinstance(item, Expression):
        return to_type(item._params[-1])

def type_from_type_str(model:Model|None, type_str: str) -> Concept:
    if type_str in python_types_str_to_concepts:
        return python_types_str_to_concepts[type_str]
    elif type_str in Concept.builtins:
        return Concept.builtins[type_str]
    elif model and type_str in model.concepts:
        concepts = model.concepts[type_str]
        if len(concepts) > 1:
            # this can be expensive, but is only done if the type_str is ambiguous
            frame = find_external_frame()
            if frame and type_str in frame.f_locals:
                c = frame.f_locals[type_str]
                if c in set(concepts):
                    return c
                else:
                    raise ValueError(f"Reference '{type_str}' is not a valid Concept")
            raise ValueError(f"Ambiguous reference to Concept '{type_str}'")
        return concepts[0]
    else:
        return Concept.builtins["Any"]

def to_name(item:Any) -> str:
    if isinstance(item, Relationship) and isinstance(item._parent, Concept):
        return f"{item._parent._name}_{item._name}"
    elif isinstance(item, (Ref, Alias)):
        return item._name or to_name(item._thing)
    elif isinstance(item, RelationshipRef):
        return item._relationship._name
    elif isinstance(item, ConceptExpression):
        return item._op._name.lower()
    elif isinstance(item, Concept):
        return item._name.lower()
    return getattr(item, "_name", "v")

def find_model(items: Any) -> Model|None:
    if isinstance(items, (list, tuple)):
        for item in items:
            model = find_model(item)
            if model:
                return model
    elif isinstance(items, dict):
        for item in items.values():
            model = find_model(item)
            if model:
                return model
    else:
        if hasattr(items, "_model") and items._model:
            return items._model
    return None

def with_source(item:Any):
    if not hasattr(item, "_source"):
        raise ValueError(f"Item {item} has no source")
    elif item._source is None:
        return {}
    elif debugging.DEBUG:
        source = item._source.to_source_info()
        if source:
            return { "file": source.file, "line": source.line, "source": source.source }
        else:
            return {"file":item._source.file, "line":item._source.line}
    else:
        return {"file":item._source.file, "line":item._source.line}



def has_keys(item: Any) -> bool:
    if isinstance(item, (list, tuple)):
        for it in item:
            if has_keys(it):
                return True

    elif isinstance(item, (Relationship, RelationshipReading)) and item._parent:
        if item.is_many():
            return True
        return has_keys(item._parent)

    elif isinstance(item, RelationshipRef):
        if item._relationship.is_many():
            return True
        return has_keys(item._parent)

    elif isinstance(item, Concept):
        if not item._is_primitive():
            return True

    elif isinstance(item, ConceptExpression):
        for it in item._params[1].values():
            if has_keys(it):
                return True
        return False

    elif isinstance(item, Ref):
        return has_keys(item._thing)

    elif isinstance(item, RelationshipFieldRef):
        return has_keys(item._relationship)

    elif isinstance(item, Alias):
        return has_keys(item._thing)

    elif isinstance(item, Aggregate):
        return len(item._group) > 0

    elif isinstance(item, Expression):
        return has_keys(item._params)

    elif isinstance(item, Data):
        return True

    elif isinstance(item, DataColumn):
        return True

    elif isinstance(item, BranchRef):
        return has_keys(item._match)

    elif isinstance(item, Match):
        pass
    elif isinstance(item, Distinct):
        pass
    elif isinstance(item, types.py_literal_types):
        pass
    else:
        raise ValueError(f"Cannot find keys for {item}")

    return False


def find_keys(item: Any, keys:OrderedSet[Any]|None = None) -> OrderedSet[Any]:
    if keys is None:
        keys = ordered_set()

    if isinstance(item, (list, tuple)):
        for it in item:
            find_keys(it, keys)

    elif isinstance(item, (Relationship, RelationshipReading)) and item._parent:
        find_keys(item._parent, keys)
        if item.is_many():
            keys.add(item._field_refs[-1])

    elif isinstance(item, RelationshipRef):
        find_keys(item._parent, keys)
        if item._relationship.is_many():
            keys.add(item._field_refs[-1])

    elif isinstance(item, Concept):
        if not item._is_primitive():
            keys.add(item)

    elif isinstance(item, ConceptExpression):
        for it in item._params[1].values():
            find_keys(it, keys)

    elif isinstance(item, Ref):
        if isinstance(item._thing, Concept):
            if not item._thing._is_primitive():
                keys.add(item)
        else:
            find_keys(item._thing, keys)

    elif isinstance(item, RelationshipFieldRef):
        find_keys(item._relationship, keys)

    elif isinstance(item, Alias):
        find_keys(item._thing, keys)

    elif isinstance(item, Aggregate):
        keys.update(item._group)

    elif isinstance(item, Expression):
        find_keys(item._params, keys)

    elif isinstance(item, Data):
        keys.add(item._row_id)

    elif isinstance(item, DataColumn):
        keys.add(item._data)

    elif isinstance(item, BranchRef):
        find_keys(item._match, keys)

    elif isinstance(item, Match):
        pass
    elif isinstance(item, Distinct):
        pass
    elif isinstance(item, types.py_literal_types):
        pass
    else:
        raise ValueError(f"Cannot find keys for {item}")

    return keys


class Key:
    def __init__(self, val:Any, is_group:bool = False):
        self.val = val
        self.is_group = is_group

def find_select_keys(item: Any, keys:OrderedSet[Key]|None = None, enable_primitive_key:bool = False) -> OrderedSet[Key]:
    if keys is None:
        keys = ordered_set()

    if isinstance(item, (list, tuple)):
        for it in item:
            find_select_keys(it, keys)

    elif isinstance(item, (Relationship, RelationshipReading)) and item._parent:
        find_select_keys(item._parent, keys)
        if item.is_many():
            keys.add( Key(item._field_refs[-1]) )

    elif isinstance(item, RelationshipRef):
        find_select_keys(item._parent, keys)
        if item._relationship.is_many():
            keys.add( Key(item._field_refs[-1]) )

    elif isinstance(item, Concept):
        if not item._is_primitive() or enable_primitive_key:
            keys.add( Key(item) )

    elif isinstance(item, ConceptExpression):
        for it in item._params[1].values():
            find_select_keys(it, keys)

    elif isinstance(item, Ref):
        if isinstance(item._thing, Concept):
            if not item._thing._is_primitive() or enable_primitive_key:
                keys.add( Key(item) )
        else:
            find_select_keys(item._thing, keys)

    elif isinstance(item, RelationshipFieldRef):
        find_select_keys(item._relationship, keys)

    elif isinstance(item, Alias):
        find_select_keys(item._thing, keys)

    elif isinstance(item, Aggregate):
        keys.update( Key(k, True) for k in item._group )

    elif isinstance(item, Expression):
        find_select_keys(item._params, keys)

    elif isinstance(item, Data):
        keys.add( Key(item._row_id) )

    elif isinstance(item, DataColumn):
        keys.add( Key(item._data) )

    elif isinstance(item, BranchRef):
        find_select_keys(item._match, keys)

    elif isinstance(item, Match):
        pass
    elif isinstance(item, Distinct):
        pass
    elif isinstance(item, types.py_literal_types):
        pass
    else:
        raise ValueError(f"Cannot find keys for {item}")

    return keys


#--------------------------------------------------
# Producer
#--------------------------------------------------

class Producer:
    def __init__(self, model:Model|None) -> None:
        self._id = next(_global_id)
        self._model = model

    #--------------------------------------------------
    # Infix operator overloads
    #--------------------------------------------------

    def _bin_op(self, op, left, right) -> Expression:
        res = Number.ref("res")
        return Expression(Relationship.builtins[op], left, right, res)

    def __add__(self, other):
        return self._bin_op("+", self, other)
    def __radd__(self, other):
        return self._bin_op("+", other, self)

    def __mul__(self, other):
        return self._bin_op("*", self, other)
    def __rmul__(self, other):
        return self._bin_op("*", other, self)

    def __sub__(self, other):
        return self._bin_op("-", self, other)
    def __rsub__(self, other):
        return self._bin_op("-", other, self)

    def __truediv__(self, other):
        return self._bin_op("/", self, other)
    def __rtruediv__(self, other):
        return self._bin_op("/", other, self)

    def __floordiv__(self, other):
        return self._bin_op("//", self, other)
    def __rfloordiv__(self, other):
        return self._bin_op("//", other, self)

    def __pow__(self, other):
        return self._bin_op("^", self, other)
    def __rpow__(self, other):
        return self._bin_op("^", other, self)

    def __mod__(self, other):
        return self._bin_op("%", self, other)
    def __rmod__(self, other):
        return self._bin_op("%", other, self)

    def __neg__(self):
        return self._bin_op("*", self, -1)

    #--------------------------------------------------
    # Filter overloads
    #--------------------------------------------------

    def _filter(self, op, left, right) -> Expression:
        return Expression(Relationship.builtins[op], left, right)

    def __gt__(self, other):
        return self._filter(">", self, other)
    def __ge__(self, other):
        return self._filter(">=", self, other)
    def __lt__(self, other):
        return self._filter("<", self, other)
    def __le__(self, other):
        return self._filter("<=", self, other)
    def __eq__(self, other) -> Any:
        return self._filter("=", self, other)
    def __ne__(self, other) -> Any:
        return self._filter("!=", self, other)

    #--------------------------------------------------
    # And/Or
    #--------------------------------------------------

    def __or__(self, other) -> Match:
        return Match(self, other)

    def __and__(self, other) -> Fragment:
        if isinstance(other, Fragment):
            return other.where(self)
        return where(self, other)

    #--------------------------------------------------
    # in_
    #--------------------------------------------------

    def in_(self, values:list[Any]|Fragment) -> Expression:
        if isinstance(values, Fragment):
            return self == values
        if not isinstance(values[0], tuple):
            values = [tuple([v]) for v in values]
        d = data(values)
        return self == d[0]

    #--------------------------------------------------
    # Relationship handling
    #--------------------------------------------------

    def _get_relationship(self, name:str) -> Relationship|RelationshipRef|RelationshipFieldRef:
        root_type:Concept = to_type(self) or Concept.builtins["Any"]
        namer = NameCache()
        r = Relationship(
            f"{{{root_type}}} has {{{name}:Any}}",
            parent=self, short_name=name, model=self._model,
            field_refs=cast(list[Ref], [root_type.ref(namer.get_name(1, root_type._name.lower())), Concept.builtins["Any"].ref(namer.get_name(2, name))])
        )
        # if we don't know the root type, then this relationship is unresolved and we're
        # really just handing an anonymous relationship back that we expect to be resolved
        # later
        if root_type is Concept.builtins["Any"]:
            r._unresolved = True
        return r

    #--------------------------------------------------
    # getattr
    #--------------------------------------------------

    def __getattr__(self, name:str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__} has no attribute {name}")
        if not hasattr(self, "_relationships"):
            return super().__getattribute__(name)

        if isinstance(self, (Concept, ConceptNew)):
            concept = self._op if isinstance(self, ConceptNew) else self
            topmost_parent = concept._get_topmost_parent()
            if (concept is not Concept.builtins['Any'] and
                not concept._is_enum() and
                name not in concept._relationships and
                not concept._has_inherited_relationship(name)):

                if self._model and self._model._strict:
                    raise AttributeError(f"{self._name} has no relationship `{name}`")
                if topmost_parent is not concept:
                    topmost_parent._relationships[name] = topmost_parent._get_relationship(name)
                    rich.print(f"[red bold][Implicit Subtype Relationship][/red bold] [yellow]{concept}.{name}[/yellow] appended to topmost parent [yellow]{topmost_parent}[/yellow] instead")

        if name not in self._relationships:
            self._relationships[name] = self._get_relationship(name)
        return self._relationships[name]

    def _has_inherited_relationship(self, name:str) -> bool:
        if isinstance(self, Concept):
            for parent in self._extends:
                if not parent._is_primitive():
                    if parent._has_relationship(name):
                        return True
        return False

    def _has_relationship(self, name:str) -> bool:
        if name in self._relationships:
            return True
        return self._has_inherited_relationship(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        elif isinstance(value, (Relationship, RelationshipReading)):
            value._parent = self
            if not value._passed_short_name:
                value._passed_short_name = name
            if name in self._relationships:
                raise ValueError(f"Cannot set attribute {name} on {type(self).__name__} a second time. Make sure to set the relationship before any usages occur")
            self._relationships[name] = value
        else:
            raise AttributeError(f"Cannot set attribute {name} on {type(self).__name__}")

    #--------------------------------------------------
    # ref + alias
    #--------------------------------------------------

    def ref(self, name:str|None=None) -> Ref|RelationshipRef:
        return Ref(self, name=name)

    def alias(self, name:str) -> Alias:
        return Alias(self, name)

    #--------------------------------------------------
    # Find model
    #--------------------------------------------------

    def _find_model(self, items:list[Any]) -> Model|None:
        if self._model:
            return self._model

        for item in items:
            if isinstance(item, (Producer, Fragment)) and item._model:
                self._model = item._model
                return item._model
        return None

    #--------------------------------------------------
    # Hash
    #--------------------------------------------------

    __hash__ = object.__hash__

    #--------------------------------------------------
    # _pprint
    #--------------------------------------------------

    def _pprint(self, indent:int=0) -> str:
        return str(self)

    #--------------------------------------------------
    # Fallbacks
    #--------------------------------------------------

    def select(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.select` not implemented")

    def where(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.where` not implemented")

    def require(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.require` not implemented")

    def define(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.then` not implemented")

#--------------------------------------------------
# Ref
#--------------------------------------------------

class Ref(Producer):
    def __init__(self, thing:Producer, name:str|None=None):
        super().__init__(thing._model)
        self._thing = thing
        self._name = name
        self._no_lookup = False
        self._relationships = {}

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef:
        rel = getattr(self._thing, name)
        return RelationshipRef(self, rel)

    def __str__(self) -> str:
        if self._name:
            return f"{self._name}{self._id}"
        return f"{self._thing}{self._id}"

class RelationshipRef(Producer):
    def __init__(self, parent:Any, relationship:Relationship|RelationshipRef, name:str|None=None):
        super().__init__(find_model([parent, relationship]))
        self._parent = parent
        if isinstance(relationship, RelationshipRef):
            relationship = relationship._relationship
        self._relationship:Relationship = relationship
        self._field_refs = [r.ref() for r in relationship._field_refs]
        if name:
            self._field_refs[-1].name = name
        self._relationships = {}

    def _get_relationship(self, name: str) -> Relationship|RelationshipRef|RelationshipFieldRef:
        rel = super()._get_relationship(name)
        if isinstance(rel, Relationship):
            return RelationshipRef(self, rel)
        elif isinstance(rel, RelationshipFieldRef):
            return RelationshipFieldRef(self, rel._relationship, rel._field_ix)
        else:
            return rel

    def __call__(self, *args: Any, **kwargs) -> Any:
        if kwargs and args:
            raise ValueError("Cannot use both positional and keyword arguments")
        if kwargs:
            # check that all fields have been provided
            clean_args = []
            for ix, field in enumerate(self._relationship._field_names):
                if field in kwargs:
                    clean_args.append(kwargs.get(field))
                if ix == 0 and self._parent:
                    continue
                if field not in kwargs:
                    raise ValueError(f"Missing argument {field}")
        else:
            clean_args = list(args)
        if len(clean_args) < self._relationship._arity():
            if self._parent:
                clean_args = [self._parent, *clean_args]
        if len(clean_args) != self._relationship._arity():
            raise ValueError(f"Expected {self._relationship._arity()} arguments, got {len(clean_args)}")
        return Expression(self._relationship, *clean_args)

    def __str__(self) -> str:
        return f"{self._parent}.{self._relationship._short_name}"

class RelationshipFieldRef(Producer):
    def __init__(self, parent:Any, relationship:Relationship|RelationshipRef|RelationshipReading, field_ix:int):
        super().__init__(find_model([relationship]))
        self._parent = parent
        if isinstance(relationship, RelationshipRef):
            relationship = relationship._relationship
        self._relationship:Relationship|RelationshipReading = relationship
        self._field_ix = field_ix
        self._relationships = {}

    @property
    def _field_ref(self) -> Ref|RelationshipRef:
        return self._relationship._field_refs[self._field_ix]

    @property
    def _concept(self) -> Concept:
        return type_from_type_str(self._model, self._relationship._fields[self._field_ix].type_str)

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef:
        rel = getattr(self._field_ref, name)
        return RelationshipRef(self, rel)

    def __call__(self, arg: Any) -> Any:
        return self == arg

    def __str__(self) -> str:
        return f"{self._relationship}.{self._field_ref}"

#--------------------------------------------------
# Concept
#--------------------------------------------------

class Concept(Producer):
    builtins = {}

    def __init__(self, name:str, extends:list[Any] = [], model:Model|None=None, identify_by:dict[str, Any]={}):
        super().__init__(model)
        self._name = name
        self._relationships = {}
        self._extends = []
        self._reference_schemes: list[tuple[Relationship|RelationshipReading, ...]] = []
        self._scheme_mapping:dict[Concept, Relationship] = {}

        for e in extends:
            if isinstance(e, Concept):
                self._extends.append(e)
            elif python_types_to_concepts.get(e):
                self._extends.append(python_types_to_concepts[e])
            else:
                raise ValueError(f"Unknown concept {e} in extends")

        if identify_by:
            scheme = []
            for k, v in identify_by.items():
                if python_types_to_concepts.get(v):
                    v = python_types_to_concepts[v]
                if isinstance(v, Concept):
                    setattr(self, k, Relationship(f"{{{self._name}}} has {{{k}:{v._name}}}", short_name=k, model=self._model))
                elif isinstance(v, type) and issubclass(v, self._model.Enum): #type: ignore
                    setattr(self, k, Relationship(f"{{{self._name}}} has {{{k}:{v._concept._name}}}", short_name=k, model=self._model))
                elif isinstance(v, Relationship):
                    self._validate_identifier_relationship(v)
                    setattr(self, k, v)
                else:
                    raise ValueError(f"identify_by must be either a Concept or Relationship: {k}={v}")
                scheme.append(getattr(self, k))
            self._reference_schemes.append(tuple(scheme))
        self._annotations = []

    def require(self, *args: Any) -> Fragment:
        return where(self).require(*args)

    def new(self, ident: Any|None=None, **kwargs) -> ConceptNew:
        self._check_ref_scheme(kwargs)
        return ConceptNew(self, ident, kwargs)

    def new_identity(self, args: Any|None=None, **kwargs: Any) -> ConceptConstruct:
        self._check_ref_scheme(kwargs, shallow=True)
        return ConceptConstruct(self, args, kwargs)

    def annotate(self, *annos:Expression|Relationship) -> Concept:
        self._annotations.extend(annos)
        return self

    #--------------------------------------------------
    # Reference schemes
    #--------------------------------------------------

    def identify_by(self, *args: Relationship|RelationshipReading):
        if not args:
            raise ValueError("identify_by requires at least one relationship")
        for rel in args:
            if not isinstance(rel, (Relationship, RelationshipReading)):
                raise ValueError(f"identify_by must be called with a Relationship/RelationshipReading, got {type(rel)}")
            else:
                self._validate_identifier_relationship(rel)
        self._reference_schemes.append(args)

    def _validate_identifier_relationship(self, rel:Relationship|RelationshipReading):
        if rel._arity() != 2:
            raise ValueError("identify_by can only be applied on binary relations")
        if rel._fields[0].type_str != self._name:
            raise ValueError("For identify_by all relationships/readings must be defined on the same Concept")

    def _ref_scheme(self, shallow=False) -> tuple[Relationship, ...] | None:
        ref_schema = []
        if not shallow:
            for parent in self._extends:
                parent_schema = parent._ref_scheme()
                if parent_schema:
                    ref_schema.extend(parent_schema)
                    break
        if self._reference_schemes:
            ref_schema.extend(self._reference_schemes[0])
        return tuple(ref_schema) if ref_schema else None

    def _check_ref_scheme(self, kwargs: dict[str, Any], shallow=False):
        scheme = self._ref_scheme(shallow)
        if not scheme:
            return
        ks = [rel._short_name for rel in scheme]
        for k in ks:
            if k not in kwargs:
                raise ValueError(f"Missing argument {k} for {self._name}")

    def _ref_scheme_hierarchy(self):
        ref_schemes = []
        for parent in self._extends:
            parent_schemes = parent._ref_scheme_hierarchy()
            if parent_schemes:
                ref_schemes.extend(parent_schemes)
                break
        if self._reference_schemes:
            ref_schemes.append({"concept": self, "scheme": self._reference_schemes[0]})

        # add mappings
        top_parent_name = ref_schemes[0]["concept"]._name if ref_schemes else None
        for ix, scheme in enumerate(ref_schemes[1:]):
            cur = scheme["concept"]
            parent = ref_schemes[ix]["concept"]
            if not self._scheme_mapping.get(parent):
                self._scheme_mapping[parent] = cur._scheme_mapping.get(parent) or Relationship(
                    f"{{{cur._name}}} to {{{top_parent_name}}}",
                    short_name=f"{cur._name}_to_{parent._name}",
                    model=self._model,
                )
            scheme["mapping"] = self._scheme_mapping[parent]

        return ref_schemes

    #--------------------------------------------------
    # Internals
    #--------------------------------------------------

    def _get_topmost_parent(self) -> Concept:
        if not self._extends:
            return self
        return self._extends[0]._get_topmost_parent()

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        relationship = self._get_parent_relationship(self, name)
        return relationship if relationship else super()._get_relationship(name)

    def _get_parent_relationship(self, root:Concept, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef | None:
        for parent in self._extends:
            if name in parent._relationships:
                return RelationshipRef(root, parent._relationships[name])
            elif not parent._is_primitive():
                return parent._get_parent_relationship(root, name)
        return None

    def _isa(self, other:Concept) -> bool:
        if self is other:
            return True
        for parent in self._extends:
            if parent._isa(other):
                return True
        return False

    def _is_primitive(self) -> bool:
        return self._isa(Primitive)

    def _is_enum(self) -> bool:
        return self._isa(Concept.builtins["Enum"])

    def _is_filter(self) -> bool:
        return False

    def __call__(self, identity:Any=None, **kwargs: Any) -> ConceptMember:
        return ConceptMember(self, identity, kwargs)

    def __str__(self):
        return self._name

#--------------------------------------------------
# ErrorConcept
#--------------------------------------------------

class ErrorConcept(Concept):
    _error_props = OrderedSet()
    _relation = None
    _overloads:dict[Concept, Relationship] = {}

    def __init__(self, name:str, extends:list[Any] = [], model:Model|None=None):
        super().__init__(name, extends, model)

    def new(self, ident: Any|None=None, **kwargs) -> ConceptNew:
        from relationalai.early_access.builder import annotations as annos
        model = kwargs.get("_model") or find_model([ident, kwargs])
        if kwargs.get("_model"):
            del kwargs["_model"]

        if not ErrorConcept._relation:
            ErrorConcept._relation = Relationship(
                "{Error} has {attribute:String} with {value:Any}",
                short_name="pyrel_error_attrs",
                model=model
            ).annotate(annos.external)
            ErrorConcept._relation._unresolved = True
        source = None
        if "_source" in kwargs:
            source = kwargs["_source"]
            del kwargs["_source"]
        else:
            source = runtime_env.get_source_pos()
        # kwargs["severity"] = "error"
        if source:
            source = source.to_source_info()
            source_id = len(errors.ModelError.error_locations)
            errors.ModelError.error_locations[source_id] = source
            kwargs["pyrel_id"] = source_id

        for k, v in kwargs.items():
            v_type = to_type(v) or python_types_to_concepts.get(type(v)) or Concept.builtins["Any"]
            if v_type and v_type not in self._overloads:
                self._overloads[v_type] = Relationship(
                    f"{{Error}} has {{attribute:String}} with {{value:{v_type._name}}}",
                    short_name="pyrel_error_attrs",
                    model=model
                ).annotate(annos.external)
            assert v_type is not None, f"Cannot determine type for {k}={v}"
            overload = self._overloads[v_type]
            if (model, k) not in ErrorConcept._error_props and not k.startswith("_"):
                ErrorConcept._error_props.add((model, k))
                with root_tracking(True):
                    frag = where(getattr(self, k)).define(
                        overload(self, k, getattr(self, k))
                    )
                    frag._model = model

        return super().new(ident, **kwargs)

    def __call__(self, identity: Any = None, **kwargs: Any) -> Any:
        raise ValueError("Errors must always be created with a new identity. Use Error.new(..) instead of Error(..)")

#--------------------------------------------------
# Builtin Concepts
#--------------------------------------------------

Primitive = Concept.builtins["Primitive"] = Concept("Primitive")
Error = Concept.builtins["Error"] = ErrorConcept("Error")

# Load builtin types
for builtin in types.builtin_types:
    if isinstance(builtin, ir.ScalarType):
        Concept.builtins[builtin.name] = Concept(builtin.name, extends=[Primitive])

Float = Concept.builtins["Float"]
Number = Concept.builtins["Number"]
Int64 = Concept.builtins["Int64"]
Int128 = Concept.builtins["Int128"]
# Integer aliases to Int128.
Integer = Concept.builtins["Int128"]
Hash = Concept.builtins["Hash"]
String = Concept.builtins["String"]
Bool = Concept.builtins["Bool"]
Date = Concept.builtins["Date"]
DateTime = Concept.builtins["DateTime"]

Decimal64 = Concept.builtins["Decimal64"]
Decimal128 = Concept.builtins["Decimal128"]
# Decimal aliases to Decimal128.
Concept.builtins["Decimal"] = Concept.builtins["Decimal128"]
Decimal = Concept.builtins["Decimal"]

# The following is a workaround for having the builtin "Int"
# but not other the builtin "Integer". The `Relationship`
# class relies upon the builtin "Integer" existing in its
# _build_inspection_fragment() method.
Concept.builtins["Int"] = Concept.builtins["Int128"]
Concept.builtins["Integer"] = Concept.builtins["Int128"]
Concept.builtins["Decimal"] = Concept.builtins["Decimal128"]

python_types_to_concepts = {
    int: Concept.builtins["Int128"],
    float: Concept.builtins["Float"],
    str: Concept.builtins["String"],
    bool: Concept.builtins["Bool"],
    date: Concept.builtins["Date"],
    datetime: Concept.builtins["DateTime"],
    PyDecimal: Concept.builtins["Decimal128"],

    Int128Dtype(): Concept.builtins["Int128"],

    # Pandas/NumPy dtype objects
    np.dtype('int64'): Concept.builtins["Int128"],
    np.dtype('int32'): Concept.builtins["Int128"],
    np.dtype('int16'): Concept.builtins["Int128"],
    np.dtype('int8'): Concept.builtins["Int128"],
    np.dtype('uint64'): Concept.builtins["Int128"],
    np.dtype('uint32'): Concept.builtins["Int128"],
    np.dtype('uint16'): Concept.builtins["Int128"],
    np.dtype('uint8'): Concept.builtins["Int128"],
    np.dtype('float64'): Concept.builtins["Float"],
    np.dtype('float32'): Concept.builtins["Float"],
    np.dtype('bool'): Concept.builtins["Bool"],
    np.dtype('object'): Concept.builtins["String"],  # Often strings are stored as object dtype

    # Pandas extension dtypes
    pd.Int64Dtype(): Concept.builtins["Int128"],
    pd.Int32Dtype(): Concept.builtins["Int128"],
    pd.Int16Dtype(): Concept.builtins["Int128"],
    pd.Int8Dtype(): Concept.builtins["Int128"],
    pd.UInt64Dtype(): Concept.builtins["Int128"],
    pd.UInt32Dtype(): Concept.builtins["Int128"],
    pd.UInt16Dtype(): Concept.builtins["Int128"],
    pd.UInt8Dtype(): Concept.builtins["Int128"],
    pd.Float64Dtype(): Concept.builtins["Float"],
    pd.Float32Dtype(): Concept.builtins["Float"],
    pd.StringDtype(): Concept.builtins["String"],
    pd.BooleanDtype(): Concept.builtins["Bool"],
}

# this map is required when we need to map standard python type string to a Concept
python_types_str_to_concepts = {
    "int": python_types_to_concepts[int],
    "float": python_types_to_concepts[float],
    "str": python_types_to_concepts[str],
    "bool": python_types_to_concepts[bool],
    "date": python_types_to_concepts[date],
    "datetime": python_types_to_concepts[datetime],
    "decimal": python_types_to_concepts[PyDecimal]
}

#--------------------------------------------------
# Relationship
#--------------------------------------------------

@dataclass(frozen=True)
class Field():
    name:str
    type_str:str

    def __str__(self):
        return f"{self.name}:{self.type_str}"

class Relationship(Producer):
    builtins = {}

    def __init__(self, madlib:str, parent:Producer|None=None, short_name:str="", model:Model|None=None, fields:list[Field]|None=None, field_refs:list[Ref]|None=None, is_many:bool|None=None, ir_relation:ir.Relation|None=None):
        found_model = model or find_model(parent) or find_model(args)
        super().__init__(found_model)
        self._parent = parent
        self._madlib = madlib
        self._passed_short_name = short_name
        self._relationships = {}
        if fields is not None:
            self._fields:list[Field] = fields
        else:
            self._fields, is_many = self._parse_schema_format(madlib)
        if not self._fields and not ir_relation:
            raise ValueError(f"No fields found in relationship {self}")
        self._ir_relation = ir_relation
        self._unresolved = False
        if field_refs is not None:
            self._field_refs = field_refs
        else:
            self._field_refs = [cast(Ref, type_from_type_str(found_model, field.type_str).ref(field.name)) for field in self._fields]
        for field in self._field_refs:
            field._no_lookup = True
        self._field_names = [field.name for field in self._fields]
        self._readings = [RelationshipReading(madlib, alt_of=self, short_name=short_name, fields=self._fields, is_many=is_many, model=found_model, parent=parent)]
        self._annotations = []
        # now that the Relationship is validated, register into the model
        if found_model is not None:
            found_model.relationships.append(self)

    @property
    def _name(self):
        return self._short_name or self._madlib

    @property
    def _short_name(self):
        return self._passed_short_name or _short_name_from_madlib(self._madlib)

    def is_many(self):
        return self._readings[0].is_many()

    def _is_filter(self) -> bool:
        return self._short_name in [">", "<", "=", "!=", ">=", "<="]

    def _parse_schema_format(self, format_string:str):
        # Pattern to extract fields like {Type*} or {name:Type*}
        pattern = r'\{([a-zA-Z0-9_]+)(\*?)(?::([a-zA-Z0-9_]+)(\*?))?\}'
        matches = re.findall(pattern, format_string)

        namer = NameCache()
        fields = []
        is_many = False
        match_index = 0
        ix = 0
        for field_name, field_name_is_many, field_type, field_type_is_many in matches:
            # If no type is specified, use the field name as the type
            if not field_type:
                field_type = field_name
                field_name = field_name.lower()
                field_type_is_many = field_name_is_many

            is_many = bool(field_type_is_many)
            if is_many and match_index != len(matches) - 1:
                raise ValueError(f"Only the last role of a relationship reading can be 1-to-many: {format_string}")

            ix += 1
            field_name = namer.get_name(ix, field_name)

            fields.append(Field(field_name, field_type))
            match_index +=1

        return fields, is_many

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        rel:RelationshipRef = getattr(self._field_refs[-1], name)
        return RelationshipRef(self, rel._relationship)

    def _arity(self):
        return len(self._fields)

    def __getattr__(self, name: str) -> Any:
        if self._arity() > 2 and name in self._field_names:
            return RelationshipFieldRef(self._parent, self, self._field_names.index(name))
        return super().__getattr__(name)

    def annotate(self, *annos:Expression|Relationship) -> Relationship:
        self._annotations.extend(annos)
        return self

    def __getitem__(self, arg:str|int|Concept) -> Any:
        return _get_relationship_item(self, arg)

    def ref(self, name:str|None=None) -> Ref|RelationshipRef:
        return RelationshipRef(self._parent, self, name=name)

    def alt(self, madlib:Any, short_name:str="", reading:RelationshipReading|None = None) -> RelationshipReading:
        if not reading:
            reading = RelationshipReading(madlib, alt_of=self, short_name=short_name, model=self._model)
        self._readings.append(reading)
        where(self(*self._field_refs)).define(
            reading._ignore_root(*reading._field_refs),
        )
        return reading

    def _build_inspection_fragment(self):
        """
        Helper function for the inspect() and to_df() methods below,
        that generates a Fragment from the Relationship, inspect()ing
        or to_df()'ing which yields all tuples in the Relationship.
        """
        field_types = [type_from_type_str(self._model, field.type_str) for field in self._fields]
        field_vars = [field_type.ref() for field_type in field_types]
        return where(self(*field_vars)).select(*field_vars)

    def inspect(self):
        return self._build_inspection_fragment().inspect()

    def to_df(self):
        return self._build_inspection_fragment().to_df()

    def __call__(self, *args: Any, **kwargs) -> Any:
        return _relationship_call(self, *args, **kwargs)

    def __str__(self):
        if self._parent and self._short_name:
            return f"{self._parent}.{self._short_name}"
        return self._name

class RelationshipReading(Producer):
    # if true, the last role has 1-many semantics
    _is_many:bool = False

    def __init__(self, madlib:str, alt_of:Relationship, short_name:str, fields:list[Field]|None=None, is_many:bool|None=None, model:Model|None=None, parent:Producer|None=None,):
        found_model = model or find_model(parent)
        super().__init__(found_model)
        self._parent = parent
        self._alt_of = alt_of
        self._madlib = madlib
        self._passed_short_name = short_name
        if fields is not None:
            self._fields:list[Field] = fields
            self._is_many = is_many or False
        else:
            self._fields, self._is_many = alt_of._parse_schema_format(madlib)
        if Counter(self._fields) != Counter(alt_of._fields):
            raise ValueError(
                f"Invalid alternative relationship. The alternative group of used fields ({', '.join(str(f) for f in self._fields)}) does not match with the original ({', '.join(str(f) for f in alt_of._fields)})")
        self._field_refs = [alt_of[f.name]._field_ref for f in self._fields]
        self._field_names = [field.name for field in self._fields]
        self._annotations = []

    def is_many(self):
        return self._is_many

    def _arity(self):
        return len(self._fields)

    def annotate(self, *annos:Expression|Relationship) -> RelationshipReading:
        self._annotations.extend(annos)
        return self

    @property
    def _name(self):
        return self._short_name or self._madlib

    @property
    def _short_name(self):
        return self._passed_short_name or _short_name_from_madlib(self._madlib)

    def _ignore_root(self, *args, **kwargs):
        expr = self(*args, **kwargs)
        expr._ignore_root = True
        return expr

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        rel:RelationshipRef = getattr(self._field_refs[-1], name)
        return RelationshipRef(self, rel._relationship)

    def __getattr__(self, name) -> Any:
        if not name.startswith("_"):
            if self._arity() > 2 and name in self._field_names:
                return RelationshipFieldRef(self._parent, self, self._field_names.index(name))
            if name not in self._alt_of._relationships:
                self._alt_of._relationships[name] = self._get_relationship(name)
            return self._alt_of._relationships[name]
        return super().__getattr__(name)

    def __getitem__(self, arg: str | int | Concept) -> Any:
        return _get_relationship_item(self, arg)

    def __call__(self, *args: Any, **kwargs) -> Any:
        return _relationship_call(self, *args, **kwargs)

    def __str__(self):
        if self._parent and self._short_name:
            return f"{self._parent}.{self._short_name}"
        return self._name

def _short_name_from_madlib(madlib:Any) -> str:
    # Replace curly braces, colons, and spaces with underscores.
    # Then strip leading/trailing underscores.
    return re.sub(r"[{}: ]", "_", str(madlib)).strip("_")

def _get_relationship_item(rel:Relationship|RelationshipReading, arg:Any) -> Any:
    if isinstance(arg, int):
        if arg < 0:
            raise ValueError(f"Position should be positive, got {arg}")
        if rel._arity() <= arg:
            raise ValueError(f"Relationship '{rel._name}' has only {rel._arity()} fields")
        return RelationshipFieldRef(rel._parent, rel, arg)
    elif isinstance(arg, str):
        if arg not in rel._field_names:
            raise ValueError(f"Relationship '{rel._name}' has only {rel._field_names} fields")
        return RelationshipFieldRef(rel._parent, rel, rel._field_names.index(arg))
    elif isinstance(arg, Concept):
        return _get_relationship_field_ref(rel, arg)
    elif isinstance(arg, type) and rel._model is not None and issubclass(arg, rel._model.Enum):
        return _get_relationship_field_ref(rel, arg._concept)
    else:
        raise ValueError(f"Unknown argument {arg}")

def _get_relationship_field_ref(rel:Relationship|RelationshipReading, concept:Concept) -> Any:
    result: RelationshipFieldRef | None = None
    for idx, ref in enumerate(rel._field_refs):
        if result is None and ref._thing._id == concept._id:
            result = RelationshipFieldRef(rel._parent, rel, idx)
        else:
            if ref._thing._id == concept._id:
                raise ValueError(
                    f"Ambiguous reference to the field: '{concept._name}' presented in more than one field. Use reference by name or position instead")
    if result is None:
        raise ValueError(f"Relationship '{rel._name}' does not have '{concept._name}' as a field")
    return result

def _relationship_call(rel:Relationship|RelationshipReading, *args: Any, **kwargs) -> Any:
    if kwargs and args:
        raise ValueError("Cannot use both positional and keyword arguments")
    if kwargs:
        # check that all fields have been provided
        clean_args = []
        for ix, field in enumerate(rel._field_names):
            if field in kwargs:
                clean_args.append(kwargs.get(field))
            if ix == 0 and rel._parent:
                continue
            if field not in kwargs:
                raise ValueError(f"Missing argument {field}")
    else:
        clean_args = list(args)
    if len(clean_args) < rel._arity():
        if rel._parent:
            clean_args = [rel._parent, *clean_args]
    if len(clean_args) != rel._arity():
        raise ValueError(f"Expected {rel._arity()} arguments, got {len(clean_args)}")
    return Expression(rel, *clean_args)

#--------------------------------------------------
# Builtin Relationships
#--------------------------------------------------

for builtin in builtins.builtin_relations + builtins.builtin_annotations:
    fields = []
    for field in builtin.fields:
        field_type = re.sub(r'[\[\{\(]', '', str(field.type)).strip()
        fields.append(f"{field.name}:{field_type}")
    args = ' '.join([f"{{{f}}}"for f in fields])
    Relationship.builtins[builtin.name] = Relationship(
        f"{builtin.name} {args}",
        parent=None,
        short_name=builtin.name,
        ir_relation=builtin,
    )

RawSource = Relationship.builtins["raw_source"]

#--------------------------------------------------
# Expression
#--------------------------------------------------

infix_ops = ["+", "-", "*", "/", "//", "^", "%", ">", ">=", "<", "<=", "=", "!="]

class Expression(Producer):
    def __init__(self, op:Relationship|RelationshipReading|Concept, *params:Any):
        super().__init__(op._model or find_model(params))
        self._op = op
        self._params = params
        self._ignore_root = False
        self._source = runtime_env.get_source_pos()

    def __str__(self):
        return f"({self._op} {' '.join(map(str, self._params))})"

    def _pprint(self, indent:int=0) -> str:
        if self._op._name in infix_ops:
            a, b = self._params[0], self._params[1]
            return f"{' ' * indent}{a} {self._op} {b}"
        return f"{' ' * indent}{self._op}({' '.join(map(str, self._params))})"

    def __getattr__(self, name: str):
        last = self._params[-1]
        if isinstance(self._op, (Relationship, RelationshipRef)) and isinstance(last, Concept):
            # lookup the last concept in the relationship, and then lookup the attribute in it
            concept = self._op.__getitem__(last)
            return getattr(concept, name)
        raise AttributeError(f"Expression has no attribute {name}")

class ConceptExpression(Expression):
    def __init__(self, con:Concept, identity:Any, kwargs:dict[str, Any]):
        super().__init__(con, identity, kwargs)
        for k, _ in kwargs.items():
            # make sure to create the properties being referenced
            getattr(self._op, k)
        self._relationships = {}

        _remove_roots([v for v in kwargs.values() if isinstance(v, Producer)])

    def _construct_args(self, scheme=None) -> dict[Relationship|Concept, Any]:
        args = {}
        scheme = scheme or self._op._ref_scheme()
        [ident, kwargs] = self._params
        if scheme:
            for rel in scheme:
                args[rel] = kwargs[rel._short_name]
        else:
            for k, v in kwargs.items():
                args[getattr(self._op, k)] = v
            if ident:
                args[self._op] = ident
        return args

    def _get_relationship(self, name: str) -> Relationship|RelationshipRef:
        parent_rel = getattr(self._op, name)
        return RelationshipRef(self, parent_rel)

    def __getattr__(self, name: str):
        return Producer.__getattr__(self, name)

class ConceptMember(ConceptExpression):
    def __init__(self, con:Concept, identity:Any, kwargs:dict[str, Any]):
        super().__init__(con, identity, kwargs)
        if identity is None:
            class_name = con._name
            raise ValueError(f"Adding or looking up an instance of Concept requires an identity. If you want to create a new identity, use {class_name}.new(..)")
        # TODO: when we do reference schemes, the identity might be
        # in a combination of kwargs rather than in the positionals


class ConceptNew(ConceptExpression):
    def __str__(self):
        return f"({self._op}.new {' '.join(map(str, self._params))})"


class ConceptConstruct(ConceptExpression):
    pass

#--------------------------------------------------
# TupleArg
#--------------------------------------------------

# There are some special relations that require an actual tuple as
# an argument. We want to differentiate that from a case where a user
# _accidentally_ passes a tuple as an argument.

class TupleArg(tuple):
    def _compile_lookup(self, compiler:Compiler, ctx:CompilerContext):
        return TupleArg(flatten([compiler.lookup(item, ctx) for item in self]))

#--------------------------------------------------
# Aggregate
#--------------------------------------------------

class Aggregate(Producer):
    def __init__(self, op:Relationship, *args: Any):
        super().__init__(op._model or find_model(args))
        self._op = op
        self._args = args
        _remove_roots(args)
        self._group = []
        self._where = where()

    def where(self, *args: Any) -> Aggregate:
        new = self.clone()
        if not new._model:
            new._model = find_model(args)
        new._where = new._where.where(*args)
        return new

    def per(self, *args: Any) -> Aggregate:
        new = self.clone()
        if not new._model:
            new._model = find_model(args)
        new._group.extend(args)
        return new

    def clone(self) -> Aggregate:
        clone = Aggregate(self._op, *self._args)
        clone._group = self._group.copy()
        clone._where = self._where
        return clone

    def __getattr__(self, name: str):
        raise AttributeError(f"Expression has no attribute {name}")

    def __str__(self):
        args = ', '.join(map(str, self._args))
        group = ', '.join(map(str, self._group))
        where = ""
        if group:
            group = f" (per {group})"
        if self._where._where:
            items = ', '.join(map(str, self._where._where))
            where = f" (where {items})"
        return f"({self._op} {args}{group}{where})"

class Group():
    def __init__(self, *args: Any):
        self._group = args

    def __str__(self):
        args = ', '.join(map(str, self._group))
        return f"(per {args})"

    #--------------------------------------------------
    # Agg funcs
    #--------------------------------------------------

    def count(self, *args: Any) -> Aggregate:
        return count(*args).per(*self._group)

    def sum(self, *args: Any) -> Aggregate:
        return sum(*args).per(*self._group)

    def avg(self, *args: Any) -> Aggregate:
        return avg(*args).per(*self._group)

    def min(self, *args: Any) -> Aggregate:
        return min(*args).per(*self._group)

    def max(self, *args: Any) -> Aggregate:
        return max(*args).per(*self._group)

#--------------------------------------------------
# Aggregate builtins
#--------------------------------------------------

def per(*args: Any) -> Group:
    return Group(*args)

def count(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["count"], *args)

def sum(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["sum"], *args)

def avg(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["avg"], *args)

def min(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["min"], *args)

def max(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["max"], *args)

class RankOrder():
    ASC = True
    DESC = False

    def __init__(self, is_asc:bool, *args: Any):
        self._is_asc = is_asc
        self._args = args

    def __str__(self):
        return f"({'asc' if self._is_asc else 'desc'} {', '.join(map(str, self._args))})"

def asc(*args: Any):
    return RankOrder(True, *args)

def desc(*args: Any):
    return RankOrder(False, *args)

def rank(*args: Any) -> Aggregate:
    # A relation is needed further down the pipeline, so we create a dummy one here.
    dummy_ir_relation = f.relation("rank", [f.field("result", types.Int128)])
    dummy_relation = Relationship(dummy_ir_relation.name, ir_relation=dummy_ir_relation)
    return Aggregate(dummy_relation, *args)

#--------------------------------------------------
# Alias
#--------------------------------------------------

class Alias(Producer):
    def __init__(self, thing:Producer, name:str):
        super().__init__(thing._model)
        self._thing = thing
        self._name = name
        self._relationships = {}
        _remove_roots([thing])

    def __str__(self) -> str:
        return f"{self._thing} as {self._name}"

#--------------------------------------------------
# Match
#--------------------------------------------------

class BranchRef(Producer):
    def __init__(self, match:Match, ix:int):
        super().__init__(match._model)
        self._match = match
        self._ix = ix

    def __str__(self):
        return f"{self._match}#{self._ix}"

class Match(Producer):
    def __init__(self, *args: Any):
        super().__init__(find_model(args))
        self._args = list(self._flatten_args(args))
        if any(isinstance(arg, Fragment) and arg._is_effect() for arg in self._args):
            _add_root(self)
        _remove_roots(args)

        # check for validity
        is_select = None
        ret_count = 0
        for arg in self._args:
            if isinstance(arg, Fragment) and arg._is_effect():
                if is_select:
                    raise ValueError("Cannot mix expression and effect clauses in a match")
                is_select = False
            elif isinstance(arg, Fragment) and not arg._is_effect():
                if is_select is False:
                    raise ValueError("Cannot mix effect and expression clauses in a match")
                is_select = True
                if ret_count == 0:
                    ret_count = len(arg._select)
                elif ret_count != len(arg._select):
                    raise ValueError("All clauses must have the same number of return values")
            elif isinstance(arg, types.py_literal_types):
                if is_select is False:
                    raise ValueError("Cannot mix then and select clauses in a match")
                is_select = True
                if ret_count == 0:
                    ret_count = 1
                elif ret_count != 1:
                    raise ValueError("All clauses must have the same number of return values")
            elif isinstance(arg, Expression) or isinstance(arg, Aggregate):
                if is_select is None:
                    is_select = True
                    if not arg._op._is_filter():
                        ret_count = 1
            elif isinstance(arg, Relationship) or isinstance(arg, Ref):
                if is_select is None:
                    is_select = True
                    ret_count = 1

        self._is_select = is_select
        self._ret_count = ret_count
        self._source = runtime_env.get_source_pos()

    def _flatten_args(self, args):
        for arg in args:
            if isinstance(arg, Match):
                for sub_arg in arg._args:
                    yield sub_arg
            else:
                yield arg

    def __iter__(self):
        for ix in range(self._ret_count):
            yield BranchRef(self, ix)

    def __str__(self):
        return " | ".join(map(str, self._args))

#--------------------------------------------------
# Union
#--------------------------------------------------

class Union(Match):
    def __str__(self):
        return " & ".join(map(str, self._args))

def union(*args: Any) -> Union:
    return Union(*args)

#--------------------------------------------------
# Negation
#--------------------------------------------------

class Not():
    def __init__(self, *args: Any):
        self._args = args
        self._model = find_model(args)
        _remove_roots(args)

    def clone(self) -> Not:
        clone = type(self)(*self._args)
        return clone

    def __str__(self):
        args_str = '\n    '.join(map(str, self._args))
        return f"(not {args_str})"

def not_(*args: Any) -> Not:
    return Not(*args)

#--------------------------------------------------
# Distinct
#--------------------------------------------------

class Distinct():
    def __init__(self, *args: Any):
        self._args = args
        self._model = find_model(args)
        _remove_roots(args)

def distinct(*args: Any) -> Distinct:
    return Distinct(*args)

#--------------------------------------------------
# Enum
#--------------------------------------------------

def create_enum_class(model):

    class ModelEnumMeta(EnumMeta):
        _concept: Concept
        def __setattr__(self, name: str, value: Any) -> None:
            if name.startswith("_") or isinstance(value, self):
                super().__setattr__(name, value)
            elif isinstance(value, (Relationship, RelationshipReading)):
                value._parent = self._concept
                if not value._passed_short_name:
                    value._passed_short_name = name
                if name in self._concept._relationships:
                    raise ValueError(
                        f"Cannot set attribute {name} on {type(self).__name__} a second time. Make sure to set the relationship before any usages occur")
                self._concept._relationships[name] = value
            else:
                raise AttributeError(f"Cannot set attribute {name} on {type(self).__name__}")

    class ModelEnum(Enum, metaclass=ModelEnumMeta):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            # this is voodoo black magic that is doing meta meta programming where
            # we are plugging into anytime a new subtype of this class is created
            # and then creating a concept to represent the enum. This happens both
            # when you do `class Foo(Enum)` and when you do `Enum("Foo", [a, b, c])`
            c = model.Concept(
                cls.__name__,
                extends=[Concept.builtins["Enum"]],
                identify_by={"name": Concept.builtins["String"]}
            )
            cls._concept = model.enum_concept[cls] = c
            model.enums[cls.__name__] = cls
            cls._has_inited_members = False

        # Python 3.10 doesn't correctly populate __members__ by the time it calls
        # __init_subclass__, so we need to initialize the members lazily when we
        # encounter the enum for the first time.
        def _init_members(self):
            if self._has_inited_members:
                return
            cls = self.__class__
            c = cls._concept
            # Add the name and value attributes to the hashes we create for the enum
            members = [
                c.new(name=name, value=value.value)
                for name, value in cls.__members__.items()
            ]
            with root_tracking(True):
                model.define(*members)
            cls._has_inited_members = True

        def _compile_lookup(self, compiler:Compiler, ctx:CompilerContext):
            self._init_members()
            concept = getattr(self.__class__, "_concept")
            return compiler.lookup(concept.new(name=self.name), ctx)

        @classmethod
        def lookup(cls, value:Producer|str):
            concept = cls._concept
            return concept.new(name=value)

    return ModelEnum

#--------------------------------------------------
# Data
#--------------------------------------------------

class DataColumn(Producer):
    def __init__(self, data:Data, _type, name:str):
        self._data = data
        self._type = _type
        self._name = name if isinstance(name, str) else f"v{name}"
        self._ref = python_types_to_concepts[_type].ref(self._name)

    def __str__(self):
        return f"DataColumn({self._name}, {self._type})"

class Data(Producer):
    def __init__(self, data:DataFrame):
        super().__init__(None)
        self._data = data
        self._relationships = {}
        self._cols = []
        self._row_id = Integer.ref("row_id")
        for col in data.columns:
            t = data[col].dtype
            self._cols.append(DataColumn(self, t, col))
            self._relationships[col] = self._cols[-1]

    def into(self, concept:Concept, keys:list[str]=[]):
        if keys:
            new = concept.new_identity(**{k.lower(): getattr(self, k) for k in keys})
        else:
            new = concept.new_identity(self._row_id)
        where(self, new).define(
            concept(new),
            *[getattr(concept, col._name)(new, col) for col in self._cols]
        )

    def __getitem__(self, item: str|int) -> DataColumn:
        if isinstance(item, int):
            return self._cols[item]
        if item in self._relationships:
            return self._relationships[item]
        raise KeyError(f"Data has no column {item}")

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        raise AttributeError(f"Data has no attribute {name}")

    def __str__(self):
        return f"Data({len(self._data)} rows, [{', '.join([str(c) for c in self._cols])}])"

    def __hash__(self):
        return hash(self._id)

def _to_df(data: DataFrame | list[tuple] | list[dict], columns:list[str]|None) -> DataFrame:
    if isinstance(data, DataFrame):
        return data
    if not data:
        return DataFrame()
    if isinstance(data, list):
        if isinstance(data[0], tuple):
            # Named tuple check
            if hasattr(data[0], '_fields'):
                return DataFrame([t._asdict() for t in data]) #type: ignore
            return DataFrame(data, columns=columns)
        elif isinstance(data[0], dict):
            return DataFrame(data)
    raise TypeError(f"Cannot convert {type(data)} to DataFrame. Use DataFrame, list of tuples, or list of dicts.")

def data(data:DataFrame|list[tuple]|list[dict], columns:list[str]|None=None) -> Data:
    return Data(_to_df(data, columns))

#--------------------------------------------------
# Fragment
#--------------------------------------------------

class Fragment():
    def __init__(self, parent:Fragment|None=None, model:Model|None=None):
        self._id = next(_global_id)
        self._select = []
        self._where = []
        self._require = []
        self._define = []
        self._order_by = []
        self._limit = 0
        self._model = parent._model if parent else model
        self._parent = parent
        self._source = runtime_env.get_source_pos()
        self._is_export = False
        self._meta = {}
        self._annotations = []
        if parent:
            self._select.extend(parent._select)
            self._where.extend(parent._where)
            self._require.extend(parent._require)
            self._define.extend(parent._define)
            self._order_by.extend(parent._order_by)
            self._limit = parent._limit

    def _add_items(self, items:PySequence[Any], to_attr:list[Any]):
        # TODO: ensure that you are _either_ a select, require, or then
        # not a mix of them
        _remove_roots(items)
        to_attr.extend(items)

        if self._define or self._require:
            if self._parent:
                _remove_roots([self._parent])
            _add_root(self)

        if not self._model:
            self._model = find_model(items)
        return self

    def where(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._where)

    def select(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._select)

    def require(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._require)

    def define(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._define)

    def order_by(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._order_by)

    def limit(self, n:int) -> Fragment:
        f = Fragment(parent=self)
        f._limit = n
        return f

    def meta(self, **kwargs: Any) -> Fragment:
        self._meta.update(kwargs)
        return self

    def annotate(self, *annos:Expression|Relationship) -> Fragment:
        self._annotations.extend(annos)
        return self

    #--------------------------------------------------
    # helpers
    #--------------------------------------------------

    def _is_effect(self) -> bool:
        return bool(self._define or self._require or (self._parent and self._parent._is_effect()))

    def _is_where_only(self) -> bool:
        return not self._select and not self._define and not self._require and not self._order_by

    #--------------------------------------------------
    # And/Or
    #--------------------------------------------------

    def __or__(self, other) -> Match:
        return Match(self, other)

    def __and__(self, other) -> Union:
        return Union(self, other)

    #--------------------------------------------------
    # Stringify
    #--------------------------------------------------

    def __str__(self):
        sections = []
        if self._select:
            select = '\n    '.join(map(str, self._select))
            sections.append(f"(select\n    {select})")
        if self._where:
            where = '\n    '.join(map(str, self._where))
            sections.append(f"(where\n    {where})")
        if self._require:
            require = '\n    '.join(map(str, self._require))
            sections.append(f"(require\n    {require})")
        if self._define:
            effects = '\n    '.join(map(str, self._define))
            sections.append(f"(then\n    {effects})")
        if self._order_by:
            order_by = '\n    '.join(map(str, self._order_by))
            sections.append(f"(order_by\n    {order_by})")
        if self._limit:
            sections.append(f"(limit {self._limit})")

        return "\n".join(sections)

    #--------------------------------------------------
    # Execute
    #--------------------------------------------------

    def __iter__(self):
        # Iterate over the rows of the fragment's results
        return self.to_df().itertuples(index=False).__iter__()

    def inspect(self):
        # @TODO what format? maybe ignore row indices?
        print(self.to_df(in_inspect=True))

    def to_df(self, in_inspect:bool=False):
        """Convert the fragment's results to a pandas DataFrame."""
        # @TODO currently this code assumes a Rel executor; should dispatch based on config

        # If there are no selects, then there are no results to return
        if not self._select:
            return DataFrame()

        qb_model = self._model or Model("anon")
        ir_model = qb_model._to_ir()
        self._source = runtime_env.get_source_pos()
        # @TODO for now we set tag to None but we need to work out how to properly propagate user-provided tag here
        with debugging.span("query", tag=None, dsl=str(self), **with_source(self), meta=self._meta) as query_span:
            query_task = qb_model._compiler.fragment(self)
            results = qb_model._to_executor().execute(ir_model, query_task)
            query_span["results"] = results
            # For local debugging mostly
            dry_run = qb_model._dry_run or bool(qb_model._config.get("compiler.dry_run", False))
            inspect_df = bool(qb_model._config.get("compiler.inspect_df", False))
            if not in_inspect and not dry_run and inspect_df:
                print(results)
            return results

    def into(self, table:Any, update:bool=False) -> None:
        from .snowflake import Table
        assert isinstance(table, Table), "Only Snowflake tables are supported for now"

        result_cols = table._col_names

        clone = Fragment(parent=self)
        clone._is_export = True
        qb_model = clone._model or Model("anon")
        ir_model = qb_model._to_ir()
        clone._source = runtime_env.get_source_pos()
        with debugging.span("query", dsl=str(clone), **with_source(clone), meta=clone._meta):
            query_task = qb_model._compiler.fragment(clone)
            qb_model._to_executor().execute(ir_model, query_task, result_cols=result_cols, export_to=table._fqn, update=update)

#--------------------------------------------------
# Select / Where
#--------------------------------------------------

def select(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).select(*args)

def where(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).where(*args)

def require(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).require(*args)

def define(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).define(*args)

#--------------------------------------------------
# Model
#--------------------------------------------------

class Model():
    def __init__(
        self,
        name: str,
        dry_run: bool = False,
        keep_model: bool = True,
        use_lqp: bool | None = None,
        use_sql: bool = False,
        strict: bool = False,
        wide_outputs: bool = False,
        config: Config | None = None,
    ):
        self._id = next(_global_id)
        self.name = f"{name}{overrides('model_suffix', '')}"
        self._dry_run = cast(bool, overrides('dry_run', dry_run))
        self._keep_model = cast(bool, overrides('keep_model', keep_model))
        self._use_sql = cast(bool, overrides('use_sql', use_sql))
        self._wide_outputs = cast(bool, overrides('wide_outputs', wide_outputs))
        self._config = config or Config()
        self._strict = cast(bool, overrides('strict', strict))
        self._use_lqp = overridable_flag('reasoner.rule.use_lqp', self._config, use_lqp, default=False)

        self.concepts:dict[str, list[Concept]] = {}
        self.relationships:list[Relationship] = []
        self.enums:dict[str, Type[Enum]] = {}
        self.enum_concept:dict[Type[Enum], Concept] = {}

        # Compiler
        self._compiler = Compiler()
        self._root_version = _global_roots.version()
        self._last_compilation = None

        # Executor
        self._executor = None

        # Enum
        self.Enum = create_enum_class(self)

    def _to_ir(self):
        if not _global_roots.has_changed(self._root_version) and self._last_compilation:
            return self._last_compilation
        self._last_compilation = self._compiler.model(self)
        self._root_version = _global_roots.version()
        return self._last_compilation

    def _to_executor(self):
        if not self._executor:
            if self._use_lqp:
                self._executor = LQPExecutor(
                    self.name,
                    dry_run=self._dry_run,
                    keep_model=self._keep_model,
                    wide_outputs=self._wide_outputs,
                )
            elif self._use_sql:
                self._executor = SnowflakeExecutor(
                    self.name,
                    self.name,
                    dry_run=self._dry_run,
                    config=self._config,
                    skip_denormalization=True,
                )
            else:
                self._executor = RelExecutor(
                    self.name,
                    dry_run=self._dry_run,
                    keep_model=self._keep_model,
                    wide_outputs=self._wide_outputs,
                    config=self._config,
                )
        return self._executor

    def Concept(self, name:str, extends:list[Concept|Any]=[], identify_by:dict[str, Any]={}) -> Concept:
        concept = Concept(name, model=self, extends=extends, identify_by=identify_by)
        if name not in self.concepts:
            self.concepts[name] = list()
        self.concepts[name].append(concept)
        return concept

    def Relationship(self, *args, short_name:str="") -> Relationship:
        return Relationship(*args, parent=None, short_name=short_name, model=self)

    def define(self, *args: Any) -> Fragment:
        return define(*args, model=self)

#--------------------------------------------------
# Compile
#--------------------------------------------------

class CompilerContext():
    def __init__(self, compiler:Compiler, parent:CompilerContext|None=None):
        self.compiler = compiler
        self.parent = parent
        self.value_map:dict[Any, ir.Value|list[ir.Var]] = parent.value_map.copy() if parent else {}
        self.items:OrderedSet[ir.Task] = OrderedSet()
        self.into_vars:list[ir.Var] = parent.into_vars.copy() if parent else []
        self.global_value_map:dict[Any, ir.Value|list[ir.Var]] = parent.global_value_map if parent else {}

    def to_value(self, item:Any, or_value=None, is_global_or_value=True) -> ir.Value|list[ir.Var]:
        if item not in self.value_map:
            if item in self.global_value_map:
                self.value_map[item] = self.global_value_map[item]
            elif or_value is not None:
                if is_global_or_value:
                    # when or_value is global save it in global_value_map as well
                    self.map_var(item, or_value)
                else:
                    self.value_map[item] = or_value
            else:
                name = to_name(item)
                qb_type = to_type(item)
                type = self.compiler.to_type(qb_type) if qb_type else types.Any
                self.map_var(item, f.var(name, type))
        return self.value_map[item]

    def map_var(self, item:Any, value:ir.Value|list[ir.Var]):
        self.global_value_map[item] = value
        self.value_map[item] = value
        return value

    def fetch_var(self, item:Any):
        if item in self.value_map:
            return self.value_map[item]
        elif item in self.global_value_map:
            return self.global_value_map[item]
        return None

    def _has_item(self, item:ir.Task) -> bool:
        return bool(item in self.items or (self.parent and self.parent._has_item(item)))

    def add(self, item:ir.Task):
        if not self._has_item(item):
            self.items.add(item)

    def try_merge_hoists(self, required: PySequence[ir.VarOrDefault], available: PySequence[ir.VarOrDefault]) -> list[ir.VarOrDefault] | None:
        avail_map = {(item.var if isinstance(item, ir.Default) else item): item for item in available}
        result = []
        for req in required:
            var = req.var if isinstance(req, ir.Default) else req
            if var not in avail_map:
                return None
            # prefer the available default as it would've bubbled up and overridden
            # the required one, otherwise take the required
            result.append(avail_map[var] if isinstance(avail_map[var], ir.Default) else req)
        return result

    def safe_wrap(self, required_hoists:PySequence[ir.VarOrDefault]) -> ir.Task:
        first = self.items[0]
        if len(self.items) == 1 and isinstance(first, ir.Logical):
            merged = self.try_merge_hoists(required_hoists, first.hoisted)
            if merged is not None:
                return f.logical(list(first.body), merged)
        return f.logical(list(self.items), required_hoists)

    def is_hoisted(self, var: ir.Var):
        return any(isinstance(i, helpers.COMPOSITES) and var in helpers.hoisted_vars(i.hoisted) for i in self.items)

    def clone(self):
        return CompilerContext(self.compiler, self)


class Compiler():
    def __init__(self):
        self.types:dict[Concept, ir.ScalarType] = {}
        self.name_to_type:dict[str, ir.Type] = {}
        self.relations:dict[Relationship|Concept|ConceptMember|RelationshipRef|RelationshipReading|ir.Relation, ir.Relation] = {}
        # cache box_type relations
        self.box_type_relations:dict[tuple[ir.Type, ir.Type], ir.Relation] = {}

    #--------------------------------------------------
    # Type/Relation conversion
    #--------------------------------------------------

    def to_annos(self, item:Concept|Relationship|RelationshipReading|Fragment) -> list[ir.Annotation]:
        annos = []
        items = item._annotations
        for item in items:
            if isinstance(item, Expression):
                ctx = CompilerContext(self)
                annos.append(f.annotation(self.to_relation(item._op), flatten([self.lookup(p, ctx) for p in item._params])))
            elif isinstance(item, Relationship):
                annos.append(f.annotation(self.to_relation(item), []))
            elif isinstance(item, ir.Annotation):
                annos.append(item)
            else:
                raise ValueError(f"Cannot convert {type(item).__name__} to annotation")
        return annos

    def to_type(self, concept:Concept) -> ir.ScalarType:
        if concept not in self.types:
            if concept._name in types.builtin_scalar_types_by_name:
                self.types[concept] = types.builtin_scalar_types_by_name[concept._name]
            else:
                parent_types = [self.to_type(parent) for parent in concept._extends]
                self.types[concept] = f.scalar_type(concept._name, parent_types, annos=self.to_annos(concept))
            self.name_to_type[concept._name] = self.types[concept]
        return self.types[concept]

    def to_relation(self, item:Concept|Relationship|RelationshipReading|RelationshipRef|ir.Relation) -> ir.Relation:
        if item not in self.relations:
            if isinstance(item, Concept):
                fields = [f.field(item._name.lower(), self.to_type(item))]
                annos = self.to_annos(item)
                builtins.builtin_annotations_by_name
                annos.append(builtins.concept_relation_annotation)
                relation = f.relation(item._name, fields, annos=annos)
            elif isinstance(item, Relationship):
                if item._ir_relation:
                    relation = item._ir_relation
                    for overload in relation.overloads:
                        self.to_relation(overload)
                else:
                    fields = []
                    for cur in item._field_refs:
                        assert isinstance(cur._thing, Concept)
                        fields.append(f.field(to_name(cur), self.to_type(cur._thing)))
                    overloads = []
                    if item._unresolved:
                        overloads = [v for k, v in self.relations.items()
                                     if isinstance(k, Relationship)
                                        and not k._unresolved
                                        and k._name == item._name]
                    relation = f.relation(item._name, fields, annos=self.to_annos(item), overloads=overloads)
                # skip the first reading since it's the same as the Relationship
                for red in item._readings[1:]:
                    self.to_relation(red)
            elif isinstance(item, RelationshipReading):
                fields = []
                for cur in item._field_refs:
                    assert isinstance(cur._thing, Concept)
                    fields.append(f.field(to_name(cur), self.to_type(cur._thing)))
                # todo: should we look for overloads in case alt_of Relationship is unresolved?
                relation = f.relation(item._name, fields, annos=self.to_annos(item))
            elif isinstance(item, RelationshipRef):
                relation = self.to_relation(item._relationship)
            elif isinstance(item, ir.Relation):
                for overload in item.overloads:
                    self.to_relation(overload)
                relation = item
            self.relations[item] = relation
            return relation
        else:
            return self.relations[item]

    #--------------------------------------------------
    # Model
    #--------------------------------------------------

    @roots(enabled=False)
    def model(self, model:Model) -> ir.Model:
        rules = []
        for concepts in model.concepts.values():
            for concept in concepts:
                if concept not in self.types:
                    self.to_type(concept)
                    self.to_relation(concept)
        unresolved = []
        for relationship in model.relationships:
            if relationship not in self.relations:
                if relationship._unresolved:
                    unresolved.append(relationship)
                else:
                    self.to_relation(relationship)
        for relationship in unresolved:
            self.to_relation(relationship)
        with debugging.span("rule_batch"):
            for idx, rule in enumerate(_global_roots):
                if not rule._model or rule._model == model:
                    meta = rule._meta if isinstance(rule, Fragment) else {}
                    with debugging.span("rule", name=f"rule{idx}", dsl=str(rule), **with_source(rule), meta=meta) as rule_span:
                        rule_ir = self.compile_task(rule)
                        rules.append(rule_ir)
                        rule_span["metamodel"] = str(rule_ir)
        root = f.logical(rules)
        engines = ordered_set()
        relations = OrderedSet.from_iterable(self.relations.values())
        types = OrderedSet.from_iterable(self.types.values())
        return f.model(engines, relations, types, root)

    #--------------------------------------------------
    # Compile
    #--------------------------------------------------

    @roots(enabled=False)
    def compile_task(self, thing:Expression|Fragment) -> ir.Task:
        if isinstance(thing, (Expression, Match, Union)):
            return self.root_expression(thing)
        elif isinstance(thing, Fragment):
            return self.fragment(thing)

    #--------------------------------------------------
    # Root expression
    #--------------------------------------------------

    @roots(enabled=False)
    def root_expression(self, item:Expression) -> ir.Task:
        ctx = CompilerContext(self)
        self.update(item, ctx)
        return f.logical(list(ctx.items))

    #--------------------------------------------------
    # Fragment
    #--------------------------------------------------

    def _is_rank(self, item) -> bool:
        return isinstance(item, Aggregate) and item._op._name == "rank"

    def _process_rank(self, items:PySequence[Expression], rank_ctx:CompilerContext):
        args_to_process = ordered_set()
        arg_is_ascending = []
        for item in items:
            if isinstance(item, RankOrder):
                args_to_process.update(item._args)
                arg_is_ascending.extend([item._is_asc] * len(item._args))
            else:
                args_to_process.add(item)
                arg_is_ascending.append(RankOrder.ASC)

        keys = ordered_set()
        for arg in args_to_process:
            if isinstance(arg, Distinct):
                continue
            keys.update(find_keys(arg))
        # Expressions go into the rank args if asked directly.
        # Otherwise they go into the projection if they are keys.
        projection = OrderedSet.from_iterable(
            flatten([self.lookup(key, rank_ctx) for key in keys], flatten_tuples=True)
        )
        args = OrderedSet.from_iterable(
            flatten([self.lookup(arg, rank_ctx) for arg in args_to_process], flatten_tuples=True)
        )
        return projection, args, arg_is_ascending

    @roots(enabled=False)
    def fragment(self, fragment:Fragment, parent_ctx:CompilerContext|None=None, into_vars:list[ir.Var] = []) -> ir.Task:
        ctx = CompilerContext(self, parent_ctx)
        if fragment._require:
            self.require(fragment, fragment._require, ctx)
        else:
            rank_var = self.order_by_or_limit(fragment, ctx)
            self.where(fragment, fragment._where, ctx)
            self.define(fragment, fragment._define, ctx)
            self.select(fragment, fragment._select, ctx, rank_var)
        return f.logical(list(ctx.items), ctx.into_vars, annos=self.to_annos(fragment))

    def order_by_or_limit(self, fragment:Fragment, ctx:CompilerContext):
        if fragment._limit == 0 and not fragment._order_by:
            return None
        if fragment._define:
            raise NotImplementedError("Order_by and/or limit are not supported on define")

        limit_ctx = ctx.clone()
        inner_ctx = limit_ctx.clone()

        # If there is an order-by, then the limit is applied on the fields there. Otherwise,
        # the limit is applied on the fields in the select (with a default ranking order).
        items = fragment._order_by if fragment._order_by else fragment._select

        projection, args, arg_is_ascending = self._process_rank(items, inner_ctx)

        limit_ctx.add(inner_ctx.safe_wrap([]))

        rank_var = f.var("v", types.Int128)
        limit_ctx.add(f.rank(list(projection), [], list(args), arg_is_ascending, rank_var, fragment._limit))
        ctx.add(f.logical(list(limit_ctx.items), [rank_var]))
        return rank_var

    def where(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        for item in items:
            self.lookup(item, ctx)

    def select(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext, rank_var:ir.Var|None=None):
        if not items:
            return

        namer = NameCache(use_underscore=False)
        aggregate_keys:OrderedSet[ir.Var] = OrderedSet()
        out_var_to_keys = {}
        fields = []
        if rank_var:
            fields.append((namer.get_name(len(fields), "rank"), rank_var))
        keys_present = has_keys(items)
        for ix, item in enumerate(items):
            # allow primitive to be a key when at least one key is present and primitive is not the last item
            # this is needed to avoid cross products in output
            enable_primitive_key = ix != len(items) - 1 if keys_present else False
            keys = find_select_keys(item, enable_primitive_key=enable_primitive_key)

            key_vars:list[ir.Var] = []
            for idx, key in enumerate(keys):
                # don't add lookups for the keys played by Concepts if they are not on the first position
                if idx > 0 and isinstance(key.val, Concept):
                    key_var = ctx.to_value(key.val)
                else:
                    key_var = self.lookup(key.val, ctx)
                assert isinstance(key_var, ir.Var)
                key_vars.append(key_var)
                if key.is_group:
                    aggregate_keys.add(key_var)

            sub_ctx = ctx.clone()
            result_vars = []
            result = self.lookup(item, sub_ctx)
            if isinstance(result, list):
                assert all(isinstance(v, ir.Var) for v in result)
                result_vars.extend(result)
            else:
                result_vars.append(result)

            extra_nullable_keys: OrderedSet[ir.Var] = OrderedSet()
            # check if whether we actually added a lookup resulting in the key, in the sub-context
            # the lookup might have already existed in the parent context, in which case the key is not nullable.
            # E.g.,
            # attends(course)
            # course = ..
            # Logical ^[..]
            #
            # vs
            #
            # Logical ^[.., course=None]
            #    attends(course)
            for it in sub_ctx.items:
                if isinstance(it, ir.Lookup):
                    vars = helpers.vars(it.args)
                    if vars[-1] in key_vars:
                        extra_nullable_keys.add(vars[-1])

            if len(sub_ctx.items) > 0:
                args = list(result_vars)
                for k in extra_nullable_keys:
                    if k not in args:
                        args.append(k)
                hoisted:list[ir.VarOrDefault] = [ir.Default(v, None) for v in args if isinstance(v, ir.Var)]
                ctx.add(sub_ctx.safe_wrap(hoisted))

            for v in result_vars:
                name = "v"
                if isinstance(item, Alias):
                    name = item._name
                elif isinstance(v, ir.Var):
                    name = v.name
                out_var_to_keys[v] = key_vars

                # if this is a nested select that is populating variables rather
                # than outputting
                if ctx.into_vars:
                    relation = self.to_relation(builtins.eq)
                    ctx.add(f.lookup(relation, [ctx.into_vars[ix], v]))
                else:
                    fields.append((namer.get_name(len(fields), name), v))

        if fields:
            annos = fragment._annotations
            if fragment._is_export:
                annos += [builtins.export_annotation]

            # If one of the vars in our output is itself a key, and it's the key of an
            # aggregation, then we should ignore its keys. This fixes the case where we
            # return the group of an aggregate and should ignore the keys of the group variables.
            final_keys = ordered_set()
            for v, keys in out_var_to_keys.items():
                if v in aggregate_keys:
                    final_keys.add(v)
                else:
                    final_keys.update(keys)

            ctx.add(f.output(fields, keys=list(final_keys), annos=annos))

    def require(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        domain_ctx = ctx.clone()
        self.where(fragment, fragment._where, domain_ctx)
        domain_vars = OrderedSet.from_iterable(flatten(list(domain_ctx.value_map.values()), flatten_tuples=True))
        to_hoist = OrderedSet()
        checks = []
        for item in items:
            req_ctx = domain_ctx.clone()
            self.lookup(item, req_ctx)
            req_body = f.logical(list(req_ctx.items))

            err_ctx = domain_ctx.clone()
            item_str = item._pprint() if isinstance(item, Producer) else str(item)
            keys = {to_name(k): k for k in find_keys(item)}
            source = item._source if hasattr(item, "_source") else fragment._source
            e = Error.new(message=f"Requirement not met: {item_str}", **keys, _source=source, _model=fragment._model)
            self.update(e, err_ctx)
            err_body = f.logical(list(err_ctx.items))
            checks.append(f.check(req_body, err_body))

            # find vars that overlap between domain and check/error and hoist them
            all_values = flatten(list(req_ctx.value_map.values()) + list(err_ctx.value_map.values()))
            to_hoist.update(domain_vars & OrderedSet.from_iterable(all_values))

        domain = f.logical(list(domain_ctx.items), list(to_hoist))
        req = f.require(domain, checks)
        ctx.add(req)

    def define(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        if len(items) == 1:
            self.update(items[0], ctx)
            return

        for item in items:
            sub_ctx = ctx.clone()
            self.update(item, sub_ctx)
            if len(sub_ctx.items) > 1:
                ctx.add(f.logical(list(sub_ctx.items)))
            elif len(sub_ctx.items) == 1:
                ctx.add(sub_ctx.items[0])

    #--------------------------------------------------
    # Reference schemes
    #--------------------------------------------------

    def relation_dict(self, items:dict[Relationship|Concept, Producer], ctx:CompilerContext) -> dict[ir.Relation, list[ir.Var]]:
        return {self.to_relation(k): unwrap_list(self.lookup(v, ctx)) for k, v in items.items()}

    def explode_ref_schemes(self, item:ConceptExpression, ctx:CompilerContext, update=False):
        hierarchy = item._op._ref_scheme_hierarchy()
        if not hierarchy:
            out = ctx.to_value(item)
            assert isinstance(out, ir.Var)
            ctx.add(f.construct(out, self.relation_dict(item._construct_args(), ctx)))
            return out

        # if we're just doing a lookup, then we only need the last reference scheme
        if not update:
            hierarchy = hierarchy[-1:]

        out = None
        for ix, info in enumerate(hierarchy):
            concept = info["concept"]
            scheme = info["scheme"]
            or_value = f.var(to_name(concept), self.to_type(concept))
            # or_value is global only when it's the last Concept in hierarchy
            is_global_or_value = ix == len(hierarchy) - 1
            cur = ctx.to_value((item, ix), or_value, is_global_or_value)
            assert isinstance(cur, ir.Var)
            ctx.add(f.construct(cur, self.relation_dict(item._construct_args(scheme), ctx)))
            if not out:
                out = cur
            if info.get("mapping"):
                rel = self.to_relation(info["mapping"])
                if out is cur:
                    out = ctx.to_value(item, f.var(to_name(concept), self.to_type(concept)))
                    assert isinstance(out, ir.Var)
                if update:
                    ctx.add(f.derive(rel, [cur, out]))
                else:
                    ctx.add(f.lookup(rel, [cur, out]))

        assert out is not None
        if update:
            for info in hierarchy:
                ctx.add(f.derive(self.to_relation(info["concept"]), [out]))
        return out

    #--------------------------------------------------
    # Lookup
    #--------------------------------------------------

    def lookup(self, item:Any, ctx:CompilerContext) -> ir.Value|list[ir.Var]:
        if isinstance(item, ConceptExpression):
            assert isinstance(item._op, Concept)
            relation = self.to_relation(item._op)
            (ident, kwargs) = item._params

            # If this is a member lookup, check that the identity is a member
            # and add all the kwargs as lookups
            if isinstance(item, ConceptMember):
                out = self.lookup(ident, ctx)
                if isinstance(out, types.py_literal_types):
                    out = f.literal(out, self.to_type(item._op))
                assert isinstance(out, (ir.Var, ir.Literal))
                if not item._op._is_primitive():
                    ctx.add(f.lookup(relation, [out]))
                rels = {self.to_relation(getattr(item._op, k)): unwrap_list(self.lookup(v, ctx))
                        for k, v in kwargs.items()}
                for k, v in rels.items():
                    assert not isinstance(v, list)
                    ctx.add(f.lookup(k, [out, v]))

                # Boxing operation on value types
                # E.g., SSN(str_var), box a String to an SSN in the IR
                op_type = self.to_type(item._op)
                if types.is_value_type(op_type):
                    inner_type = out.type
                    if inner_type == op_type:
                        return out
                    new_out = f.var(to_name(item._op), op_type)
                    ctx.add(f.lookup(builtins.cast, [op_type, out, new_out]))
                    self.relations[item] = builtins.cast
                    out = new_out

                return out

            # otherwise we have to construct one
            out = self.explode_ref_schemes(item, ctx, update=False)
            return out

        elif isinstance(item, Expression):
            params = [self.lookup(p, ctx) for p in item._params]
            relation = self.to_relation(item._op)
            ctx.add(f.lookup(relation, flatten(params)))
            return params[-1]

        elif isinstance(item, Concept):
            v = ctx.to_value(item)
            if not item._isa(Primitive):
                assert isinstance(v, ir.Var)
                relation = self.to_relation(item)
                ctx.add(f.lookup(relation, [v]))
            return v

        elif isinstance(item, (Relationship, RelationshipRef, RelationshipReading)):
            params = item._field_refs
            if item._parent:
                params = [item._parent] + params[1:]
            return self.lookup(item(*params), ctx)

        elif isinstance(item, RelationshipFieldRef):
            rel = item._relationship
            params = list(rel._field_refs)
            if item._parent:
                params = [item._parent] + params[1:]
            self.lookup(rel(*params), ctx)
            return self.lookup(params[item._field_ix], ctx)

        elif isinstance(item, Ref):
            if item._no_lookup:
                return ctx.to_value(item)

            root = item._thing
            prev_mapping = ctx.to_value(root)
            out = ctx.to_value(item)
            ctx.map_var(root, out)
            self.lookup(root, ctx)
            ctx.map_var(root, prev_mapping)
            return out

        elif isinstance(item, Alias):
            return self.lookup(item._thing, ctx)

        elif isinstance(item, Aggregate):
            relation = self.to_relation(item._op)

            group = [self.lookup(g, ctx) for g in item._group]
            group = [item for item in flatten(group, flatten_tuples=True) if isinstance(item, ir.Var)]

            agg_ctx = ctx.clone()

            # additional wheres
            self.where(item._where, item._where._where, agg_ctx)

            if self._is_rank(item):
                # The rank output is always an int
                out = agg_ctx.to_value(item, f.var(to_name(item), types.Int128))
                assert isinstance(out, ir.Var)

                projection, args, arg_is_ascending = self._process_rank(item._args, agg_ctx)
                internal_vars = ordered_set()

                ir_node = f.rank(projection.get_list(), group, args.get_list(), arg_is_ascending, out)

            else:
                out = agg_ctx.to_value(item)
                assert isinstance(out, ir.Var)
                arg_count = len(relation.fields) - 1 # skip the result
                raw_args = flatten([self.lookup(a, agg_ctx) for a in item._args])

                # the projection includes all keys for the args
                projection = [self.lookup(key, agg_ctx) for key in find_keys(item._args)]
                # the projection is also all raw_args that aren't consumed by the agg
                projection += raw_args[:-arg_count] if arg_count else raw_args
                projection = flatten(projection, flatten_tuples=True)
                projection = list(dict.fromkeys([item for item in projection if isinstance(item, ir.Var)]))

                # agg args + result var
                args = raw_args[-arg_count:] if arg_count else []
                args.append(out)

                internal_vars = set(flatten(raw_args + projection, flatten_tuples=True))
                ir_node = f.aggregate(relation, projection, group, args)

            final_ctx = ctx.clone()
            if agg_ctx.items:
                internal = internal_vars - set(flatten(list(ctx.value_map.values()), flatten_tuples=True))
                hoisted = [ir.Default(v, None) for v in internal if isinstance(v, ir.Var)]
                hoisted.sort(key=lambda x: x.var.name)
                final_ctx.add(f.logical(list(agg_ctx.items), list(hoisted)))
            final_ctx.add(ir_node)
            ctx.add(f.logical(list(final_ctx.items), [out]))
            return out

        elif isinstance(item, Not):
            not_ctx = ctx.clone()
            for a in item._args:
                self.lookup(a, not_ctx)
            ctx.add(f.not_(f.logical(list(not_ctx.items))))

        elif isinstance(item, Fragment):
            if item._is_where_only():
                for where in item._where:
                    self.lookup(where, ctx)
                return None

            sub_ctx = ctx.clone()

            # if we encounter a select and we aren't already trying to write
            # it into vars, add some
            into_vars = ctx.into_vars
            if not len(into_vars) and item._select:
                into_vars = sub_ctx.into_vars = flatten([ctx.to_value(s) for s in item._select])

            ctx.add(self.fragment(item, sub_ctx))
            out = None
            if len(into_vars) == 1:
                out = into_vars[0]
            elif len(into_vars) > 1:
                out = into_vars
            elif len(item._select) == 1:
                out = sub_ctx.to_value(item._select[0])
            elif len(item._select) > 1:
                out = flatten([sub_ctx.to_value(s) for s in item._select])

            return out

        elif isinstance(item, (Match, Union)):
            branches = []
            vars = []
            if item._is_select:
                vars = ctx.fetch_var(item)
                if isinstance(vars, ir.Var):
                    vars = [vars]
                elif not vars:
                    vars = [f.var(f"v{i}") for i in range(item._ret_count)]
                    ctx.map_var(item, vars)
                assert isinstance(vars, list)
                for branch in item._args:
                    branch_ctx = ctx.clone()
                    branch_ctx.into_vars = vars
                    v = self.lookup(branch, branch_ctx)
                    if not isinstance(v, list):
                        v = [v]
                    for var, ret in zip(vars, v):
                        if var is not ret:
                            relation = self.to_relation(builtins.eq)
                            branch_ctx.add(f.lookup(relation, [var, ret]))
                    branches.append(branch_ctx.safe_wrap(vars))
            else:
                for branch in item._args:
                    branch_ctx = ctx.clone()
                    self.update(branch, branch_ctx)
                    branches.append(branch_ctx.safe_wrap([]))
            if isinstance(item, Union):
                ctx.add(f.union(branches, vars))
            else:
                ctx.add(f.match(branches, vars))

            return vars or None

        elif isinstance(item, BranchRef):
            vars = ctx.value_map.get(item._match)
            if not vars:
                self.lookup(item._match, ctx)
                vars = ctx.value_map.get(item._match)
            assert isinstance(vars, list)
            return vars[item._ix]

        elif isinstance(item, Group):
            for g in item._group:
                self.lookup(g, ctx)

        elif isinstance(item, Distinct):
            vs = [self.lookup(v, ctx) for v in item._args]
            return flatten(vs)

        elif isinstance(item, Data):
            refs = [item._row_id] + [i._ref for i in item._cols]
            vars = flatten([self.lookup(v, ctx) for v in refs])
            ctx.add(f.data(item._data, vars))
            return vars[0]

        elif isinstance(item, DataColumn):
            self.lookup(item._data, ctx)
            return ctx.to_value(item._ref)

        elif isinstance(item, types.py_literal_types):
            return item

        elif item is None:
            return None

        elif isinstance(item, (ir.Var, ir.Literal)):
            return item

        elif hasattr(item, "_compile_lookup"):
            return item._compile_lookup(self, ctx)

        else:
            raise ValueError(f"Cannot lookup {item}, {type(item)}")

    #--------------------------------------------------
    # Update
    #--------------------------------------------------

    def update(self, item:Expression|Match|Union, ctx:CompilerContext) -> ir.Value|list[ir.Var]:
        if isinstance(item, ConceptExpression):
            assert isinstance(item._op, Concept)
            relation = self.to_relation(item._op)
            (ident, kwargs) = item._params
            out = ctx.to_value(item)
            assert isinstance(out, ir.Var)

            # if this is a member lookup, then our out var is just the identity passed in
            if isinstance(item, ConceptMember):
                out = self.lookup(ident, ctx)
                assert not isinstance(out, list)
                ctx.map_var(item, out)
            # otherwise we have to construct one
            else:
                out = self.explode_ref_schemes(item, ctx, update=True)

            ctx.add(f.derive(relation, [out]))
            # derive the membership and all the relationships
            rels = self.relation_dict({getattr(item._op, k): v for k, v in kwargs.items()}, ctx)
            for k, v in rels.items():
                assert not isinstance(v, list)
                ctx.add(f.derive(k, [out, v]))
            return out

        elif isinstance(item, Expression) and item._op is Relationship.builtins["="]:
            if isinstance(item._params[0], (Relationship, RelationshipRef)):
                return self.update(item._params[0](item._params[1]), ctx)
            elif isinstance(item._params[1], (Relationship, RelationshipRef)):
                return self.update(item._params[1](item._params[0]), ctx)
            elif isinstance(item._params[0], RelationshipFieldRef) or isinstance(item._params[1], RelationshipFieldRef):
                raise ValueError("Cannot set fields of a multi-field relationship individually")
            else:
                raise ValueError("Cannot set a non-relationship via ==")

        elif isinstance(item, Expression):
            op = item._op
            params = flatten([self.lookup(p, ctx) for p in item._params])
            # the case when root a relationship populated thought a reading
            if isinstance(op, RelationshipReading) and not item._ignore_root:
                op = item._op._alt_of
                # reuse params for the root relationship
                ref_2_param = {ref: param for ref, param in zip(item._op._field_refs, params)}
                params = flatten([ref_2_param[ref] for ref in op._field_refs])
            relation = self.to_relation(op)
            ctx.add(f.derive(relation, params))
            return params[-1]

        elif isinstance(item, Fragment):
            self.lookup(item, ctx)

        elif isinstance(item, (Match, Union)):
            self.lookup(item, ctx)

        elif hasattr(item, "_compile_update"):
            return item._compile_update(self, ctx)

        else:
            raise ValueError(f"Cannot update {item}")

__all__ = ["select", "where", "require", "define", "distinct", "per", "count", "sum", "min", "max", "avg"]

#--------------------------------------------------
# Todo
#--------------------------------------------------
"""
- Syntax
    ✔ construct
    ✔ static data handling
    ✔ Fix fragments to not be chained
    ✔ Extends
    ✔  Quantifiers
        ✔ not
        ✔ exists
        ✔ forall
    ✔ Aggregates
    ✔ Require
    ✘ Multi-step chaining
    ✔ ref
    ✔ alias
    ✔ match
    ✔ union
    ✔ capture all rules
    ✔ implement aliasing
    ✔ support defining relationships via madlibs Relationship("{Person} was born on {birthday:Date}")
    ✔ distinct
    ☐ nested fragments
    ✔  handle relationships with multiple name fields being accessed via prop:
        Package.shipment = Relationship("{Package} in {Shipment} on {Date}")
        Package.shipment.date, Package.shipment.shipment, Package.shipment.package
    ☐  sources
        ☐  table
        ☐  csv

- Compilation
    ✔ simple expressions
    ✔ select
    ✔ then
    ✔ Quantifiers
        ✔ exists
        ✔ forall
        ✔ not
    ✔ Aggregates
        ✔ Determine agg keys from inputs
        ✔ Group
    ✔ Require
    ✔ Alias
    ✔ Ref
    ✔ Match
    ✔ Union
    ✔ whole model
    ✔ distinct
    ✔ add Else to hoists
    ✔ where(..).define(Person.coolness == 10)
    ☐ extends
        ☐ nominals
    ✔ have require find keys and return the keys in the error
    ☐ Match/union with multiple branch refs in a select, duplicates the whole match
    ☐ nested fragments

☐ Execution
    ✔ basic queries
    ✔ query when iterating over a select
    ☐ debugger hookup
    ☐ table sources
    ☐ graph index
    ☐ exports
    ☐ config overhaul

"""
