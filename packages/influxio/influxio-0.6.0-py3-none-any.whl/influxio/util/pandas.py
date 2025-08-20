from contextlib import contextmanager
from unittest.mock import patch

from pandas.io.sql import SQLTable

_create_table_setup_dist = SQLTable._create_table_setup


@contextmanager
def sqlalchemy_table_kwargs(**kwargs):
    def _create_table_setup(self):
        table = _create_table_setup_dist(self)
        table.kwargs.update(kwargs)
        return table

    with patch("pandas.io.sql.SQLTable._create_table_setup", _create_table_setup):
        yield
