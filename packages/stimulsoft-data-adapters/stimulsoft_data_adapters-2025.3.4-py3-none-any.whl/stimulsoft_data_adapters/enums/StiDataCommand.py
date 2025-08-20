from enum import Enum


class StiDataCommand(Enum):

    NONE = None
    GET_SUPPORTED_ADAPTERS = 'GetSupportedAdapters'
    GET_SCHEMA = 'GetSchema'
    GET_DATA = 'GetData'
    TEST_CONNECTION = 'TestConnection'
    RETRIEVE_SCHEMA = 'RetrieveSchema'
    EXECUTE = 'Execute'
    EXECUTE_QUERY = 'ExecuteQuery'


### Helpers

    @staticmethod
    def getValues():
        return [enum.value for enum in StiDataCommand if enum.value != None]