"""
BibTeX reference management format, for LaTeX formatting.
Note: Unchanged copy.
"""

import json
from logging import getLogger

log = getLogger(__name__)


def convert_bibtex(metadata_record: dict) -> str:
    """Generate output string in BibTex format.

    Note:
        Converter is only valid for the metadata schema for EnviDat.

    Args:
        metadata_record (dict): Individual EnviDat metadata entry record dictionary.

    Returns:
        str: string in BibTeX format

    """
    try:
        return bibtex_convert_dataset(
            metadata_record,
        )
    except AttributeError as e:
        log.error(e)
        log.error("Cannot convert package to BibTeX format.")
        raise AttributeError("Failed to convert package to BibTeX format.")


def bibtex_convert_dataset(dataset: dict) -> str:
    """Create the BibTeX string from API dictionary."""
    # name as identifier (plus year later)
    name = dataset["name"]
    converted_package = "@misc { " + name

    # year (add to name) and journal
    publication = json.loads(dataset.get("publication", "{}"))
    publication_year = publication["publication_year"]

    converted_package += f"-{publication_year}"
    converted_package += f',\n\t year = "{publication_year}"'
    publisher = publication["publisher"]
    converted_package += f',\n\t publisher = "{publisher}"'

    # title
    title = dataset["title"]
    converted_package += ',\n\t title = "' + title + '"'

    # author
    authors = json.loads(dataset.get("author", "[]"))
    author_names = []
    for author in authors:
        author_name = ""
        if author.get("given_name"):
            author_name += author["given_name"].strip() + " "
        author_names += [author_name + author["name"]]
    bibtex_author = " and ".join(author_names)
    converted_package += f',\n\t author = "{bibtex_author}"'

    # DOI
    doi = dataset.get("doi", "").strip()
    if doi:
        converted_package += f',\n\t DOI = "http://dx.doi.org/{doi}"'

    # url
    package_name = dataset.get("name", "")
    url = f"https://www.envidat.ch/dataset/{package_name}"
    converted_package += ',\n\t url = "' + url + '"'

    # close bracket
    converted_package += "\n\t}"

    return converted_package
