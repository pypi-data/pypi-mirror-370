"""Constants used in converters"""

from enum import Enum


class EnviDatConverter(str, Enum):
    """Names of converters available to convert EnviDat packages to external formats."""

    DATACITE = "datacite"
    JSONLD = "jsonld"
    RIS = "ris"
    DIF = "dif"
    ISO = "iso"
    BIBTEX = "bibtex"
    DCATAP = "dcat-ap"
    SIGNPOSTING = "signposting"


class InputTypes(str, Enum):
    """Names of types available to convert EnviDat packages to external formats."""

    DOI = "doi"
    ID = "id"


class ConverterExtension(str, Enum):
    """
    File extensions for output files created by converters available to convert EnviDat
    packages to external formats.
    """

    DATACITE = "xml"
    JSONLD = "json"
    RIS = "ris"
    DIF = "xml"
    ISO = "xml"
    BIBTEX = "bib"
    DCATAP = "xml"
    SIGNPOSTING = "json"
