"""
Helper methods for realated items and related identifiers conversion.
"""

import os
import re
import requests
import validators

## THESE ARE STILL TO BE REDONE


def get_doi(word: str) -> str | None:
    """Get DOI string from input word string, if DOI not found then returns None.

    Example:
        an input of "https://doi.org/10.1525/cse.2022.1561651" would return
        "10.1525/cse.2022.1561651" as output

    Args:
        word (str): Input string to test if it contains a DOI

    Returns:
        str: String of DOI
        None: If DOI could not be found
    """
    doi = None

    # Apply search criteria to find DOIs
    search_strings = ["doi", "10."]
    if any(search_str in word for search_str in search_strings):
        # Assign doi if "10." in word
        doi_start_index = word.find("10.")
        if doi_start_index != -1:
            doi = word[doi_start_index:]

            # Remove unwanted trailing period characters if they exist
            unwanted_chars = [".", ","]
            if any(doi[-1] == char for char in unwanted_chars):
                doi = doi[:-1]

    # Return DOI if it exists, else return None
    return doi


# TODO possibly pass env config as argument
def get_envidat_doi(
    word: str,
    api_host="https://envidat.ch",
    api_package_show="/api/action/package_show?id=",
) -> str | None:
    """Get DOI string from input work by calling EnviDat API,
         if DOI not found then returns None.

    Example:
        An input of
        "https://www.envidat.ch/#/metadata/amphibian-and-landscape-data-swiss-lowlands"
        would return ""10.16904/envidat.267" as output

    Args:
        word (str): Input string to test if it contains a DOI retrieved from
                    EnviDat CKAN API
        api_host (str): API host URL. Attempts to get from environment.
            Default value is "https://envidat.ch".
        api_package_show (str): API host path to show package. Attempts to get from
             environment. Default value is "/api/action/package_show?id="

    Returns:
        str: String of DOI
        None: If DOI could not be found
    """
    doi = None

    # Check if word meets search criteria to be an EnviDat package URL
    if (
        word.startswith(
            ("https://www.envidat.ch/#/metadata/", "https://www.envidat.ch/dataset/")
        )
        and "/resource/" not in word
    ):
        # Extract package_name from package URL
        last_slash_index = word.rfind("/")
        if last_slash_index != -1:
            package_name = word[(last_slash_index + 1) :]

            # Extract environment variables from config, else use default values
            api_host = os.getenv("API_HOST", default=api_host)
            api_package_show = os.getenv("API_PACKAGE_SHOW", default=api_package_show)

            # Assemble URL used to call EnviDat CKAN API
            api_url = f"{api_host}{api_package_show}{package_name}"

            # Call API and try to return doi
            try:
                data = get_url(api_url).json()
                if data:
                    doi = data.get("result").get("doi")
                    if doi:
                        return doi
            except Exception:
                return None

    return doi


def get_dora_doi(word: str) -> str | None:
    """Get DOI string from input word string by calling DORA API,
         if DOI not found then returns None.

    Example:
        an input of "https://www.dora.lib4ri.ch/wsl/islandora/object/wsl%3A3213"
        would return "10.5194/tc-10-1075-2016" as output.

    Args:
        word (str): Input string to test if it contains a DOI retrieved from DORA API

    Returns:
        str: String of DOI
        None: If DOI could not be found
    """
    doi = None

    # Apply search criteria to find DOIs from DORA API
    # DORA API documentation:
    # https://www.wiki.lib4ri.ch/display/HEL/Technical+details+of+DORA
    dora_str = "dora.lib4ri.ch/wsl/islandora/object/"
    if dora_str in word:
        dora_start_index = word.find(dora_str)
        dora_pid = word[(dora_start_index + len(dora_str)) :]

        # Remove any characters that may exist after DORA PID
        dora_end_index = dora_pid.find("/")

        # Modify dora_pid if dora_end_index found in dora_pid
        if dora_end_index != -1:
            dora_pid = dora_pid[:dora_end_index]

        # Call DORA API and get DOI if it listed in citation
        doi_dora = get_dora_doi_string(dora_pid)
        if doi_dora:
            doi = doi_dora

    return doi


def get_dora_doi_string(
    dora_pid: str, dora_api_url: str = "https://envidat.ch/dora"
) -> str | None:
    """Get DOI string from WSL DORA API using DORA PID.

    DORA API documentation:
    https://www.wiki.lib4ri.ch/display/HEL/Technical+details+of+DORA

    ASSUMPTION: Only one DOI exists in each DORA API record "citation" key

    Args:
        dora_pid (str): DORA PID (permanent identification)
        dora_api_url (str): API host url. Attempts to get from environment.
            Defaults to "https://envidat.ch/dora"

    Returns:
        str: String of DOI
        None: If DOI could not be found
    """
    # Extract environment variables from config, else use default values
    dora_api_url = os.getenv("DORA_API_URL", default=dora_api_url)

    # Replace '%3A' ASCII II code with semicolon ':'
    dora_pid = re.sub("%3A", ":", dora_pid)

    # Replace literal asterisk "\*" with empty string ""
    dora_pid = re.sub("\\*", "", dora_pid)

    # Assemble url used to call DORA API
    dora_url = f"{dora_api_url}/{dora_pid}"

    try:
        data = get_url(dora_url).json()

        if data:
            citation = data[dora_pid]["citation"]["WSL"]

            for word in citation.split(" "):
                # Return DOI if it exists
                doi = get_doi(word)
                if doi:
                    return doi

            # If DOI not found then return None
            return None

        return None

    except Exception:
        return None


def get_url(url: str) -> requests.Response:
    """Get a URL with additional error handling.

    Args:
        url (str): The URL to GET.
    """
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r
    except Exception as e:
        print(e)

    return None


def get_dc_related_identifiers(
    related_identifiers: str, has_related_datasets=False
) -> list[dict[str, str]]:
    """Return EnviDat records "related_datasets" or "related_publications" values in
    DataCite "relatedIdentifiers" tag format.

    Note:
        "relatedIdentiferType" and "relationType" are required attributes
        for each "relatedIdentifer"

    Args:
        related_identifiers (str): Input related idetifiers, expected input is from
            "related_datasets" or "related_publications" keys.
        has_related_datasets (bool): If true then input is assumed to be from
            "related_datasets" value in EnviDat record.
            Default value is false and is assumed to correspond to
            "related_publications" value in EnviDat record.
    """
    # Assign relation_type
    if has_related_datasets:
        # Corresponds to "related_datasets" key
        relation_type = "Cites"
    else:
        # Corresponds to "related_publications" key
        relation_type = "IsSupplementTo"

    # Assign empty list to contain related identifiers
    dc_related_identifiers = []

    # Validate related_identifiers
    if related_identifiers:
        # Remove special characters "\r", "\n" and
        # remove Markdown link syntax using brackets and parentheses
        # and replace with one space " "
        related_identifiers = re.sub(r"\r|\n|\[|\]|\(|\)", " ", related_identifiers)

        # Assign empty array to hold "related_ids" values that will be used to check for
        # duplicates
        related_ids = []

        # Extract DOIs
        for word in related_identifiers.split(" "):
            # Apply search function to find DOIs
            doi = get_doi(word)

            # If not doi then apply DORA API DOI search function
            if not doi:
                doi = get_dora_doi(word)

            # If not doi then apply EnviDat CKAN API DOI search function
            if not doi:
                doi = get_envidat_doi(word)

            # Add doi to dc_related_identifiers if it meets conditions
            if doi and "/" in doi and doi not in related_ids:
                related_ids.append(doi)

                dc_related_identifiers += [
                    {
                        "#text": doi,
                        "@relatedIdentifierType": "DOI",
                        "@relationType": relation_type,
                    }
                ]

                continue

            # Apply URL validator to find other URLs (that are not DORA or EnviDat DOIs)
            is_url = validators.url(word)

            # Add URL to dc_related_identifiers if it meets conditions
            if all(
                [
                    is_url,
                    word not in related_ids,
                    "doi" not in word,
                    "dora.lib4ri.ch/wsl/islandora/object/" not in word,
                ]
            ):
                related_ids.append(word)

                dc_related_identifiers += [
                    {
                        "#text": word,
                        "@relatedIdentifierType": "URL",
                        "@relationType": relation_type,
                    }
                ]

    return dc_related_identifiers


def get_dc_related_identifiers_resources(resources) -> list[dict[str, str]]:
    """Return URLs from resources in DataCite "relatedIdentifier" tag format.

    Note:
        "relatedIdentiferType" and "relationType" are required attributes
        for each "relatedIdentifer"
    """
    dc_related_identifier = []

    for resource in resources:
        resource_url = resource.get("url", "")
        if resource_url:
            dc_related_identifier += [
                {
                    "#text": resource_url,
                    "@relatedIdentifierType": "URL",
                    "@relationType": "IsRequiredBy",
                }
            ]

    return dc_related_identifier
