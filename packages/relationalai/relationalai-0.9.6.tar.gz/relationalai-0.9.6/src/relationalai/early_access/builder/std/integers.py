from __future__ import annotations

from .. import builder as b

# Coerce a number to Int64.
def int64(value: b.Producer|int) -> b.ConceptMember:
    return b.ConceptMember(b.Int64, value, {})

# Coerce a number to Int128.
def int128(value: b.Producer|int) -> b.ConceptMember:
    return b.ConceptMember(b.Int128, value, {})
