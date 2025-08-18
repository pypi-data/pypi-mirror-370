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
        if option == "host":
            if request.config.getoption(option_name) == "localhost":
                return request.config.getini(option_name)
            elif request.config.getini(option_name) == "localhost":
                return request.config.getoption(option_name)
        elif option == "port":
            if request.config.getoption(option_name) == 3306:
                return request.config.getini(option_name)
            elif request.config.getini(option_name) == 3306:
                return request.config.getoption(option_name)
        elif option == "username":
            if request.config.getoption(option_name) == "root":
                return request.config.getini(option_name)
            elif request.config.getini(option_name) == "root":
                return request.config.getoption(option_name)
        elif option == "charset":
            if request.config.getoption(option_name) == "utf8":
                return request.config.getini(option_name)
            elif request.config.getini(option_name) == "utf8":
                return request.config.getoption(option_name)
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