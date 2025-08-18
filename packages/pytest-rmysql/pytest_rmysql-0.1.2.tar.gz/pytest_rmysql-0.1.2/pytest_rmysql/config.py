from typing import TypedDict, Any
from _pytest.fixtures import FixtureRequest


class MySQLConfig(TypedDict):
    host: str
    port: int
    database: str
    username: str
    password: str
    # params: str
    charset: str

def parse_config(request: FixtureRequest) -> MySQLConfig:
    def get_option(option: str) -> Any:
        option_name = "rmysql_" + option
        return request.config.getoption(option_name) or request.config.getini(option_name)

    config : MySQLConfig = {
        'host': get_option('host'),
        'port': get_option('port'),
        'database': get_option('database'),
        'username': get_option('username'),
        'password': get_option('password'),
        # 'params': get_option('params'),
        'charset': get_option('charset'),
    }

    return config