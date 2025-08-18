import pymysql
import pytest

from pytest_rmysql.config import parse_config


@pytest.fixture(scope='session')
def rmysql(request):
    config = parse_config(request)
    mysql_conn = pymysql.connect(
        host=config.get('host'),
        port=config.get('port'),
        user=config.get('username'),
        password=config.get('password'),
        database=config.get('database'),
        charset=config.get('charset'),
    )
    mysql_conn.connect()
    mysql_conn.cursor().execute("select 1")

    yield mysql_conn

    mysql_conn.close()
