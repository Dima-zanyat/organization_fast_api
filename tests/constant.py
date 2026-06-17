"""Файл для констант pytest."""

CREATE_DEPARTMENT_URL = "/departments"
GET_DEPARTMENTS_TREE_URL = "/departments/1"
CREATE_EMPLOYEES_URL = "/departments/1/employees"
PATCH_DEPARTMENT = "/departments/"
DELETE_DEPARTMENT = "/departments/"

# Department
BASE_DEPARTMENT_NAME = "BASE_DEPARTMENT"
SUB_DEPARTMENT_NAME = "SUB_DEPARTMENT"

# EMPLOYE
NAME_EMPLOYE = "TEST_USER"
POSITION_EMPLOYE = "TESTER"


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
BASE_URL_TEST = "http://test"


TEST_DEPTH = 1

# Query_param
MODE_DELETE_CASCADE = "cascade"
MODE_DELETE_REASSIGN = "reassign"
