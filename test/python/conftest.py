import numpy
import os
import pytest
import shutil
from os.path import abspath
import glob
import duckdb
from typing import Union, Optional
from duckdb import DuckDBPyConnection

dir = os.path.dirname(os.path.abspath(__file__))
build_type = "release"

@pytest.fixture(scope="function")
def duckdb_empty_cursor(request):
    connection = duckdb.connect('')
    cursor = connection.cursor()
    return cursor

def add_extension(extension_name, conn: Union[str, DuckDBPyConnection] = '') -> DuckDBPyConnection:
    if (isinstance(conn, str)):
        config = {
            'allow_unsigned_extensions' : 'true'
        }
        conn = duckdb.connect(conn or '', config=config)
    file_path = f"'{dir}/../../duckdb/build/{build_type}/extension/{extension_name}/{extension_name}.duckdb_extension'"
    conn.execute(f"LOAD {file_path}")
    return conn

@pytest.fixture(scope="function")
def require():
    def _require(extension_name, db_name=''):
        conn = add_extension(extension_name, db_name)
        return conn

    return _require

@pytest.fixture(scope='function')
def connection():
	return add_extension('substrait')

@pytest.fixture(scope='session', autouse=True)
def duckdb_cursor(request):

    connection = duckdb.connect('')
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE integers (i integer)')
    cursor.execute('INSERT INTO integers VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9),(NULL)')
    cursor.execute('CREATE TABLE timestamps (t timestamp)')
    cursor.execute("INSERT INTO timestamps VALUES ('1992-10-03 18:34:45'), ('2010-01-01 00:00:01'), (NULL)")
    cursor.execute("CALL dbgen(sf=0.01)")
    return cursor


@pytest.fixture(scope="function")
def duckdb_cursor_autocommit(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        duckdb.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    connection = duckdb.connect(test_dbfarm)
    connection.set_autocommit(True)
    cursor = connection.cursor()
    return (cursor, connection, test_dbfarm)


@pytest.fixture(scope="function")
def initialize_duckdb(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        duckdb.shutdown()
        if tmp_path.is_dir():
            shutil.rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    duckdb.connect(test_dbfarm)
    return test_dbfarm
