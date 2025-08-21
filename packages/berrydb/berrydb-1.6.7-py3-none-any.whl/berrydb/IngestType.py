from enum import Enum

class IngestType(Enum):
    """Enumeration for different types of ingest sources"""
    URL = "Url"
    FILE = "File"
