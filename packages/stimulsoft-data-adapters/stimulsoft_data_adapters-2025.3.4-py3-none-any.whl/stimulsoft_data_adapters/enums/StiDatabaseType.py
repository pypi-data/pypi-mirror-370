from enum import Enum


class StiDatabaseType(Enum):

    NONE = None

    # File
    XML = 'XML'
    JSON = 'JSON'
    CSV = 'CSV'

    # SQL
    MYSQL = 'MySQL'
    MSSQL = 'MS SQL'
    POSTGRESQL = 'PostgreSQL'
    FIREBIRD = 'Firebird'
    ORACLE = 'Oracle'
    ODBC = 'ODBC'

    # NoSQL
    MONGODB = 'MongoDB'


### Helpers

    @staticmethod
    def getValues():
        return [enum.value for enum in StiDatabaseType if enum.value != None]