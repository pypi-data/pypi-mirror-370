from enum import Enum

class IngestFileType(Enum):
    """Enumeration for different types of files that can be ingested"""
    PDF = "PDF"
    XLSX = "XLSX"
    HTML = "HTML"