from typing import Any

from relationalai.early_access.builder import annotations, Relationship as QBRelationship


class AssertedRelation(QBRelationship):
    """
    A relation that's assumed to be defined in the target system, but cannot be verified.

    This is used as a common parent class for such relations, and the compiler makes sure to
    not generate any unnecessary constructs for them.
    """

    def __init__(self, model, name: str, *sig: Any):
        args = [f'{{_x_{idx}:{typ}}}' for idx, typ in enumerate(sig)]
        madlib = f'{name} {" ".join(args)}'
        super().__init__(madlib, short_name=name, model=model.qb_model())
        self.annotate(annotations.external)
        self._dsl_model = model
