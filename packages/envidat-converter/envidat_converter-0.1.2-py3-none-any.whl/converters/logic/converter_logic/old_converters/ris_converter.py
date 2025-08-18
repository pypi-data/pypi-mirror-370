"""
Council information system (RIS) of the municipal council of Zurich.
Note: Unchanged copy
"""

import json
from logging import getLogger

log = getLogger(__name__)


def convert_ris(metadata_record: dict) -> str:
    """Generate output string in RIS format.

    Note:
        Converter is only valid for the metadata schema for EnviDat.

    Args:
        metadata_record (dict): Individual EnviDat metadata entry record dictionary.

    Returns:
        str: string in RIS format

    """
    try:
        return ris_convert_dataset(metadata_record)
    except ValueError as e:
        log.error(e)
        log.error("Cannot convert package to RIS format.")
        raise ValueError("Failed to convert package to RIS format.")


def ris_convert_dataset(dataset_dict: dict) -> str:
    """Create the RIS string from API dictionary."""
    ris_list = []

    #   TY  - DATA
    ris_list += ["TY  - DATA"]

    #   T1  - Title
    title = dataset_dict["title"]
    ris_list += ["T1  - " + title]

    #   AU  - Authors
    authors = json.loads(dataset_dict.get("author", "[]"))
    for author in authors:
        author_name = ""
        if author.get("given_name"):
            author_name += author["given_name"].strip() + " "
        author_name += author["name"].strip()
        ris_list += ["AU  - " + author_name]

    #   DO  - DOI
    doi = dataset_dict.get("doi", "").strip()
    if doi:
        ris_list += ["DO  - " + doi]

    #   UR  - dataset url as information
    package_name = dataset_dict.get("name", "")
    package_url = f"https://www.envidat.ch/dataset/{package_name}"
    ris_list += ["UR  - " + package_url]

    #   KW  - keywords
    keywords = get_keywords(dataset_dict)
    for keyword in keywords:
        ris_list += ["KW  - " + keyword]

    #   PY  - publication year
    publication = json.loads(dataset_dict.get("publication", "{}"))
    publication_year = publication["publication_year"]
    ris_list += ["PY  - " + publication_year]

    #   PB  - Publisher
    publisher = publication["publisher"]
    ris_list += ["PB  - " + publisher]

    #   LA  - en
    language = dataset_dict.get("language", "en").strip()
    if len(language) <= 0:
        language = "en"
    ris_list += ["LA  - " + language]

    #   ER  -
    ris_list += ["ER  - "]

    return ris_list


def get_keywords(data_dict: dict):
    """Extract keywords from tags."""
    keywords = []
    for tag in data_dict.get("tags", []):
        name = tag.get("display_name", "").upper()
        keywords += [name]
    return keywords
