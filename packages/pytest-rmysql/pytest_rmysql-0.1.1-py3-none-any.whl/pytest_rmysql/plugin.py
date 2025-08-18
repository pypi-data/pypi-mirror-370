from pytest_rmysql import fixtures
def pytest_addoption(parser):
    """plugin configuration in .ini"""
    parser.addini(name='rmysql_host', type='string', help="MySQL host", default='localhost')

    parser.addini(name='rmysql_port', type='int', default=3306, help="MySQL port")

    parser.addini(name='rmysql_database', type='string', help="MySQL database name", default=None)

    parser.addini(name='rmysql_user', type='string', help="MySQL user name", default=None)

    parser.addini(name='rmysql_password', type='string', help="MySQL password", default=None)

    # parser.addini(name='rmysql_params', type='string', help="MySQL parameters", default="")

    parser.addini(name='rmysql_charset', type='string', help="MySQL charset", default="UTF-8")

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
        default="UTF-8",
        help="MySQL charset"
    )

    rmysql = fixtures.rmysql