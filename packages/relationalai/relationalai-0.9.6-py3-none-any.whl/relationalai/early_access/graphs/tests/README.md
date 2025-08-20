Regrettably, an interaction between an assertion in Loaders
and python packing oddities prevents us from consolidating
the tests for this package into this directory, at least for now.

To work around that issue, the tests live in
    tests/early_access/graphs

The failure mode for posterity:
```
(.venv) graphs % pytest -k 'kite'
ImportError while loading conftest '/[]...]/relationalai-python/src/relationalai/early_access/graphs/tests/conftest.py'.
../../__init__.py:12: in <module>
    from .loaders import csv
../../loaders/csv.py:195: in <module>
    CSVLoader.register_for_extensions(".csv", ".tsv")
../../loaders/loader.py:111: in register_for_extensions
    cls.register()
../../loaders/loader.py:106: in register
    assert cls.type not in Loader.type_to_loader or Loader.type_to_loader[cls.type] == cls, f"{cls.__name__} has the same type '{cls.type}' as another loader ({Loader.type_to_loader[cls.type].__name__})."
E   AssertionError: CSVLoader has the same type 'csv' as another loader (CSVLoader).
```