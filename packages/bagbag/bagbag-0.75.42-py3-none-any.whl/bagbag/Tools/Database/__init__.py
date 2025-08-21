from typing import TYPE_CHECKING
from lazy_imports import LazyImporter
import sys

_import_structure = {
    "src": [
        "SQLite",
        "MySQL",
        "mySQLSQLiteKeyValueTable",
        "mySQLSQLiteTable",
        "mySQLSQLiteQueue",
        "mySQLSQLiteConfirmQueue",
    ]
}

if TYPE_CHECKING:
    from .src import (
        SQLite,
        MySQL,
        mySQLSQLiteKeyValueTable,
        mySQLSQLiteTable,
        mySQLSQLiteQueue,
        mySQLSQLiteConfirmQueue,
    )
else:
    sys.modules[__name__] = LazyImporter(
        __name__,
        globals()["__file__"],
        _import_structure,
        extra_objects={},
    )


