import dataclasses
import datetime
from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional, TypeVar, Generic, Tuple, Callable, Sequence
from typing import Union

import relationalai.early_access.builder as qb
from relationalai.early_access.builder import std
from relationalai.early_access.builder.builder import Not
from relationalai.early_access.dsl.orm.relationships import Relationship, Role
from relationalai.early_access.dsl.orm.types import Concept
from relationalai.early_access.dsl.snow.common import ColumnRef, ForeignKey

_PrimitiveType = Union[int, float, str, bool, datetime.date, datetime.datetime, Enum]
FilterBy = Union[_PrimitiveType, Not, qb.Expression, tuple[qb.Expression]]

_BuiltInQbTransformer = Callable  # A callable that is a built-in QB transformer, such as string_trim, lowercase, etc.
_Transformer = Union[_BuiltInQbTransformer, qb.Relationship]
TransformWith = Union[_Transformer, Sequence[_Transformer]]

_supported_builtins_to_types = {
    std.strings.lower: (qb.String, qb.String),
    std.strings.upper: (qb.String, qb.String),
}

def _get_transform_types(obj: _Transformer):
    """Utility: return (input_type, output_type) of a transformer/relationship."""
    if isinstance(obj, qb.Relationship) and obj._arity() == 2:
        fields = getattr(obj, "_field_refs", None)
        if fields:
            return fields[0]._thing, fields[-1]._thing
    elif isinstance(obj, Callable) and obj in _supported_builtins_to_types:
        input_type, output_type = _supported_builtins_to_types[obj]
        return input_type, output_type
    raise ValueError(f"Cannot infer input/output types from {obj}. Make sure to use a valid built-in transformer or"
                     f" a binary relationship")

def _validate_transform_with(transform_with: Optional[TransformWith], input_type: Optional[qb.Concept]=None):
    if not transform_with:
        return

    elements = (transform_with,) if not isinstance(transform_with, tuple) else transform_with

    # Check the chain of types
    prev_output_type = input_type
    for idx, elem in enumerate(elements):
        if not isinstance(elem, (qb.Relationship , Callable)):
            raise ValueError(f"Expected a built-in transformer or a binary relationship, got {type(elem)}")
        input_type, output_type = _get_transform_types(elem)
        if prev_output_type is not None:
            if input_type is not prev_output_type:
                raise ValueError(f"Type mismatch during transformation: output of #{idx-1} ({prev_output_type}) !="
                                 f" input of #{idx} ({input_type})")
        prev_output_type = output_type

# defining symbol in codegen to not expose this to the user
Symbol = Concept.builtins["Symbol"]


class BindableTable(ABC):
    """
    A class representing a bindable table.
    """

    @abstractmethod
    def key_type(self) -> qb.Concept:
        pass

    @abstractmethod
    def physical_name(self) -> str:
        pass


class BindableAttribute(ABC):

    @property
    @abstractmethod
    def table(self) -> BindableTable:
        pass

    @abstractmethod
    def physical_name(self) -> str:
        pass

    @abstractmethod
    def type(self) -> qb.Concept:
        pass

    @property
    @abstractmethod
    def references_column(self) -> Optional[ColumnRef]:
        pass

    @abstractmethod
    def column_ref(self) -> ColumnRef:
        pass

    @abstractmethod
    def decimal_scale(self) -> Optional[int]:
        pass

    @abstractmethod
    def decimal_size(self) -> Optional[int]:
        pass


@dataclasses.dataclass(frozen=True)
class Binding:
    """
    Base class for all bindings in the model. It captures the column and the optional filter that should be applied
    to the binding.

    Examples of filters:
        - `FilterBy` can be a primitive value, such as an integer or a string, which will be used to filter the
          values in the column.
        - An expression can be used to filter the values in the column based on a more complex condition.
        - A tuple of expressions can be used to filter the values in the column based on multiple expressions, joined
          together.

        Note: all the expressions must be atomic, i.e., they cannot contain arbitrarily nested formulas.

        # binds the column to the role in the relationship, filtering out any rows that don't match the specified value
        {source}.COLUMN.binds(MyRelationship, filter_by="some_value")

        # binds the column to the role in the relationship, filtering out any rows that don't match the specified
        # expression
        {source}.COLUMN.binds(MyRelationship, filter_by=(
            {source}.ANOTHER_COLUMN >= 18
        ))

        # multiple atoms can be used too, resulting in a conjunction
        {source}.COLUMN.binds(MyRelationship[MyRole], filter_by=(
            {source}.ANOTHER_COLUMN >= 18,
            {source}.YET_ANOTHER_COLUMN == "some_value"
        ))

    Examples of transformations:
        - `TransformWith` can be a QB built-in like `trim` or `lower`.
        - A single *binary* relationship can be used to transform the values in the column, where the type of the value
          must follow the data type defined in the model for the role.
        - A tuple of relationships can be used to transform the values in the column, chaining the transformations.
          The types should chain and match, with the last one being the data type defined in the model for the role.

        # single string lowercase transformation
        {source}.COLUMN.binds(MyRelationship, transform_with=std.strings.lower)

        # chain of transformations with a trim followed by an uppercase
        {source}.COLUMN.binds(MyRelationship, transform_with=(
            std.strings.trim, std.strings.upper
        ))

        # manually defined transformation relationship
        my_transformer = Relationship("MyTransformer {String} {String}")
        s1, s2 = String.ref(), String.ref()
        define(my_transformer(s1, s2)).where(
            # ... implement the logic ...
        )

        {source}.COLUMN.binds(MyRelationship, transform_with=my_transformer)
    """
    column: 'BindableColumn'
    filter_by: Optional[FilterBy]
    transform_with: Optional[TransformWith]


@dataclasses.dataclass(frozen=True)
class RoleBinding(Binding):
    """
    RoleBinding represents a binding between a column and a role in a relationship.

    See `BindableColumn.binds` for more details on how to use this binding.
    """
    role: Role

    def __str__(self):
        return f'RoleBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.role.player().name()}]'


@dataclasses.dataclass(frozen=True)
class AbstractConceptBinding(Binding):
    """
    Represents a parent class for all concept bindings. Doesn't have any specific semantics but serves as a base
    class for this class hierarchy.
    """
    entity_type: qb.Concept


@dataclasses.dataclass(frozen=True)
class IdentifierConceptBinding(AbstractConceptBinding):
    """
    Represents a binding between an identifier column and a specific entity type.

    This binding could either represent a constructor binding (instances of the entity type are constructed from the
    values), referent binding (instances of the entity type are being looked up by the values), or a subtype binding
    (instances are being looked up using the parent type's ref scheme, or it acts as a constructor for the subtype).

    See `BindableColumn.identifies` and `BindableColumn.references` for more details on how to use this binding.
    """

    def __str__(self):
        return f'IdentifierConceptBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.entity_type.name()}]'


@dataclasses.dataclass(frozen=True)
class ReferentConceptBinding(AbstractConceptBinding):
    """
    Represents a binding between an identifier column and a specific entity type, where the values in the column
    are used to look up existing instances of the entity type.

    See `BindableColumn.identifies` and `BindableColumn.references` for more details on how to use this binding.
    """

    def __str__(self):
        return f'ReferentConceptBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.entity_type.name()}]'


@dataclasses.dataclass(frozen=True)
class SubtypeConceptBinding(AbstractConceptBinding):
    """
    Represents a binding between an identifier column and a subtype of an entity type, where the values in the column
    are used to filter existing instances of the parent entity type. That could be done either directly (any value from
    that column is a subtype) or with the extra filter passed in `filter_by`, by filtering out the rows that do not
    match the specified value.

    See `BindableColumn.binds_subtype` for more details on how to use this binding.
    """

    def __str__(self):
        return f'SubtypeConceptBinding[{self.column.table.physical_name()}:{self.column.physical_name()} -> {self.entity_type.name()}]'


class BindableColumn(BindableAttribute, qb.Relationship, ABC):
    _source: BindableTable
    _references_column: Optional[ColumnRef]

    def __init__(self, col_name: str, col_type: qb.Concept, source: BindableTable, model):
        madlib, short_name = self._construct_name(col_name, col_type, source)
        qb.Relationship.__init__(self, madlib, model=model.qb_model(), short_name=short_name)
        self._col_name = col_name
        self._type = col_type
        self._source = source
        self._orm_model = model
        self._references_column = None

    @abstractmethod
    def _construct_name(self, col_name: str, col_type: qb.Concept, source: BindableTable) -> Tuple[str, str]:
        pass

    def identifies(self, entity_type: Concept, filter_by: Optional[FilterBy] = None,
                   transform_with: Optional[TransformWith] = None):
        """
        Binds a column that identifies an entity type. With that, the values in the column are used to construct
        instances of the entity type.

        Examples:
            {source}.ID.identifies(Person) # binds the column values to the Person entity type, constructing instances
        """
        if isinstance(entity_type, Enum):
            raise ValueError(f'Cannot bind to Enum {entity_type}, use `references` instead')
        _validate_transform_with(transform_with, input_type=self._type)
        binding = IdentifierConceptBinding(column=self, entity_type=entity_type, filter_by=filter_by,
                                           transform_with=transform_with)
        self._orm_model.binding(binding)

    def references(self, entity_type: Concept, filter_by: Optional[FilterBy] = None,
                   transform_with: Optional[TransformWith] = None):
        """
        Binds a column that references an identifier of an entity type. With that, the values in the column are
        used to look up existing instances of the entity type.

        Examples:
            {source}.ID.identifies(Person) # binds the column values to the Person entity type, constructing instances
            {another_source}.PERSON_ID.references(Person) # binds the column values to the Person entity type,
                                                          # looking up existing instances

            {source}.TRACKING_NUMER.identifies(TrackingNumber) # constructs instances of the TrackingNumber entity type
            {source}.RETURN_TRACKING_NUMBER.references(TrackingNumber) # looks up existing instances of the TrackingNumber entity type
        """
        _validate_transform_with(transform_with, input_type=self._type)
        binding = ReferentConceptBinding(column=self, entity_type=entity_type, filter_by=filter_by,
                                         transform_with=transform_with)
        self._orm_model.binding(binding)

    def binds_subtype(self, sub_type: Concept, filter_by: Optional[FilterBy] = None,
                      transform_with: Optional[TransformWith] = None):
        """
        Binds a column that contains identifier of the subtype. The values in the column are used to filter
        existing instances of the parent entity type by filtering out the rows that do not match the
        specified value.

        Note: the subtype must inherit the reference scheme of the parent entity type and not define its own. Otherwise,
        use `identifies` or `references` to bind to the subtype.

        Examples:
            # constructs instances of the CorporateAction entity type
            {source}.CORPORATE_ACTION_ID.identifies(CorporateAction)

            # partitions CorporateAction into Split subtype
            {source}.CORPORATE_ACTION_ID.binds_subtype(Split, filter_by=(
                {source}.CORPORATE_ACTION_TYPE == "SPLIT"
            ))

            # partitions CorporateAction into Merger subtype
            {source}.CORPORATE_ACTION_ID.binds_subtype(Merger, filter_by=(
                {source}.CORPORATE_ACTION_TYPE == "MERGER"
            ))
        """
        _validate_transform_with(transform_with, input_type=self._type)
        binding = SubtypeConceptBinding(column=self, entity_type=sub_type, filter_by=filter_by,
                                        transform_with=transform_with)
        self._orm_model.binding(binding)

    def binds(self, elm, filter_by: Optional[FilterBy] = None, transform_with: Optional[TransformWith] = None):
        """
        Binds the column to a role in a relationship or a role itself. It's possible to bind a column to a binary
        relationship, which will bind to the last role in the relationship.

        Examples:
            {source}.{column}.binds(MyRelationship) # binds the last role in MyRelationship

            {source}.{column}.binds(MyRelationship[MyConcept]) # binds the role played by MyConcept (if unique)

            # binding by index (may be useful for relationships with multiple roles played by the same concept)
            # BecameFriendsAt = Relationship("{Person} at {DateTime} befriended {Person}")
            friends_source.PERSON_ID.binds(BecameFriendsAt[0]) # binds the first Person role
            friends_source.BEFRIENDED_AT.binds(BecameFriendsAt[DateTime]) # binds the DateTime role
            friends_source.FRIEND_ID.binds(BecameFriendsAt[2]) # binds the second Person role (third in the relationship)
        """
        if isinstance(elm, Relationship):
            # this binds to the last role in binary relations
            if elm._arity() > 2:
                raise ValueError(f'Expected binary or unary relationship, got arity {elm._arity()}')
            roles = elm._roles()
            role = roles[-1]
        elif isinstance(elm, Role):
            role = elm
        else:
            raise Exception(
                f'Expected ORM Relationship or Role, got {type(elm)} - QB Relationships cannot be used in bindings')
        _validate_transform_with(transform_with, input_type=self._type)
        binding = RoleBinding(role=role, column=self, filter_by=filter_by, transform_with=transform_with)
        self._orm_model.binding(binding)

    @property
    def table(self):
        return self._source

    @property
    def references_column(self) -> Optional[ColumnRef]:
        return self._references_column

    @references_column.setter
    def references_column(self, ref: ColumnRef):
        self._references_column = ref

    def physical_name(self) -> str:
        return self._col_name

    def type(self) -> qb.Concept:
        return self._type

    def column_ref(self) -> ColumnRef:
        return ColumnRef(self._source.physical_name(), self.physical_name())


T = TypeVar("T", bound=BindableColumn)
class AbstractBindableTable(BindableTable, Generic[T], ABC):
    _foreign_keys: set[ForeignKey]

    def __init__(self, name: str, model, foreign_keys: set[ForeignKey]):
        super().__init__()
        self._table = name
        self._model = model
        self._cols: dict[str, T] = dict()
        self._foreign_keys = foreign_keys

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        if key in self._cols:
            return self._cols[key]
        raise AttributeError(f'Table "{self.physical_name()}" has no column named "{key}"')

    def foreign_key(self, *refs: Tuple[BindableColumn, BindableColumn]):
        source_columns = []
        target_columns = []

        for source, target in refs:
            source_columns.append(ColumnRef(source.table.physical_name(), source.physical_name()))
            target_columns.append(ColumnRef(target.table.physical_name(), target.physical_name()))

        source_col_names = "_".join(col.column for col in source_columns)
        target_col_names = "_".join(col.column for col in target_columns)

        fk_name = f"fk_{source_col_names}__to__{target_col_names}"

        fk = ForeignKey(fk_name, source_columns, target_columns)
        self._foreign_keys.add(fk)
        self._process_foreign_key(fk)

    def key_type(self) -> qb.Concept:
        return qb.Integer

    def columns(self):
        return self._cols

    def _process_foreign_keys(self):
        for fk in self._foreign_keys:
            self._process_foreign_key(fk)

    def _process_foreign_key(self, fk):
        # TODO : this doesn't work for composite FKs
        for col in fk.source_columns:
            target_col = fk.target_columns[0]
            self._cols[col.column].references_column = target_col
