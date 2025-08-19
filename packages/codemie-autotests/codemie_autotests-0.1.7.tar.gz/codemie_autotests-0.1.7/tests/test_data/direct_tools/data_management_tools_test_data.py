from tests.enums.tools import DataManagementTool, Toolkit
from tests.enums.integrations import DataBaseDialect

sql_tools_test_data = [
    (
        Toolkit.DATA_MANAGEMENT,
        DataManagementTool.SQL,
        DataBaseDialect.MY_SQL,
        {"sql_query": "SHOW TABLES"},
        [{"Tables_in_my_database": "products"}, {"Tables_in_my_database": "users"}],
    ),
    (
        Toolkit.DATA_MANAGEMENT,
        DataManagementTool.SQL,
        DataBaseDialect.POSTGRES,
        {
            "sql_query": "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        },
        [{"table_name": "users"}, {"table_name": "products"}],
    ),
]
