from .enums.StiDatabaseType import StiDatabaseType
from .enums.StiDataType import StiDataType
from .StiFileAdapter import StiFileAdapter


class StiXmlAdapter(StiFileAdapter):
    
### Properties

    version = '2025.3.4'
    """Current version of the data adapter."""

    checkVersion = True
    """Sets the version matching check on the server and client sides."""

    type = StiDatabaseType.XML
    dataType = StiDataType.XML
