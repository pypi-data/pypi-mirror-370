import pymysql
import pytest
from pytest_rmysql.config import parse_config


def pytest_addoption(parser):
    """plugin configuration in .ini"""
    parser.addini(name='rmysql_host', help="MySQL host", default='localhost')

    parser.addini(name='rmysql_port', default=3306, help="MySQL port")

    parser.addini(name='rmysql_database', help="MySQL database name", default=None)

    parser.addini(name='rmysql_user', help="MySQL user name", default=None)

    parser.addini(name='rmysql_password', help="MySQL password", default=None)

    # parser.addini(name='rmysql_params',  help="MySQL parameters", default="")

    parser.addini(name='rmysql_charset', help="MySQL charset", default="utf8")

    """plugin configuration in cmd"""
    group = parser.getgroup('rmysql', 'RMySQL plugin')
    group.addoption(
        "--rmysql-host",
        type=str,
        default="localhost",
        help="MySQL host"
    )
    group.addoption(
        "--rmysql-port",
        type=int,
        default=3306,
        help="MySQL port"
    )
    group.addoption(
        "--rmysql-username",
        type=str,
        default="root",
        help="MySQL username"
    )
    group.addoption(
        "--rmysql-password",
        type=str,
        default=None,
        help="MySQL password"
    )
    group.addoption(
        "--rmysql-database",
        type=str,
        default=None,
        help="MySQL database name"
    )
    # group.addoption(
    #     "--rmysql-params",
    #     type=str,
    #     default="",
    #     help="MySQL parameters"
    # )
    group.addoption(
        "--rmysql-charset",
        type=str,
        default="utf8",
        help="MySQL charset"
    )

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