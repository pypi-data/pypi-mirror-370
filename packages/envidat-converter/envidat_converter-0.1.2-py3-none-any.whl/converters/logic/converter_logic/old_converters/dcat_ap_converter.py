"""
DCAT-AP CH for OpenDataSwiss.
Note: Unchanged copy
"""

import json
import logging
from collections import OrderedDict
from typing import Union

from dateutil.parser import parse as parse_date
from xmltodict import parse, unparse

log = logging.getLogger(__name__)


def convert_dcat_ap(metadata_records: Union[dict, list[dict]]) -> str:
    """Generate output string in DCAT-AP format.

    Accepts a single metadata entry, or list of entries.

    Note:
        Converter is only valid for the metadata schema for EnviDat.

    Args:
        metadata_records (dict, list[dict]):
            Either:
                - Individual EnviDat metadata entry dictionary.
                - List of EnviDat metadata record dictionaries.

    Returns:
        str: string in DCAT-AP CH XML format.
    """
    try:
        if isinstance(metadata_records, list):
            converted_records = []
            for record in metadata_records:
                converted_records.append(
                    dcat_ap_convert_dataset(
                        record,
                    )
                )
            return wrap_packages_dcat_ap_xml(converted_records)

        return wrap_packages_dcat_ap_xml(
            dcat_ap_convert_dataset(
                metadata_records,
                as_xml=True,
            )
        )
    except AttributeError as e:
        log.error(e)
        log.error("Cannot convert package to DCAT-AP format.")
        raise AttributeError("Failed to convert package to DCAT-AP format.")


def dcat_ap_convert_dataset(
    metadata_record: dict, as_xml: bool = False
) -> Union[str, dict]:
    """Generate output string in DCAT-AP format.

    Note:
        Converter is only valid for the metadata schema for EnviDat.

    Args:
        metadata_record (dict): Individual EnviDat metadata entry record dictionary.
        as_xml (bool): If set, unparse dictionary to XML string.

    Returns:
        (str, dict):
            Either:
                - XML string in DCAT-AP format, if as_xml=True.
                - Dictionary in DCAT-AP format, for further processing.

    """
    md_metadata_dict = OrderedDict()

    # Dataset URL
    package_name = metadata_record["name"]
    package_url = f"https://www.envidat.ch/#/metadata/{package_name}"
    md_metadata_dict["dcat:Dataset"] = {"@rdf:about": package_url}

    # identifier
    package_id = metadata_record["id"]
    md_metadata_dict["dcat:Dataset"]["dct:identifier"] = f"{package_id}@envidat"

    # title
    title = metadata_record["title"]
    md_metadata_dict["dcat:Dataset"]["dct:title"] = {
        "@xml:lang": "en",
        "#text": title,
    }

    # description
    description = clean_text(metadata_record.get("notes", ""))
    md_metadata_dict["dcat:Dataset"]["dct:description"] = {
        "@xml:lang": "en",
        "#text": description,
    }

    # issued
    creation_date = metadata_record.get("metadata_created")
    if creation_date:
        md_metadata_dict["dcat:Dataset"]["dct:issued"] = {
            "@rdf:datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
            "#text": parse_date(creation_date).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    # modified
    modification_date = metadata_record.get("metadata_modified", creation_date)
    if modification_date:
        md_metadata_dict["dcat:Dataset"]["dct:modified"] = {
            "@rdf:datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
            "#text": parse_date(modification_date).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    # publication (MANDATORY)
    md_metadata_dict["dcat:Dataset"]["dct:publisher"] = {
        "foaf:Organization": {
            "@rdf:about": "https://envidat.ch/#/about",
            "foaf:name": "EnviDat",
        }
    }

    # landing page
    md_metadata_dict["dcat:Dataset"]["dcat:landingPage"] = {
        "@rdf:resource": package_url
    }

    # contact point (MANDATORY)
    maintainer = json.loads(metadata_record.get("maintainer", "{}"))
    maintainer_name = ""

    if maintainer.get("given_name"):
        maintainer_name += maintainer["given_name"].strip() + " "

    maintainer_name += maintainer["name"]
    maintainer_email = "mailto:" + maintainer["email"]
    individual_contact_point = {
        "vcard:Individual": {
            "vcard:fn": maintainer_name,
            "vcard:hasEmail": {"@rdf:resource": maintainer_email},
        }
    }

    if maintainer_email == "mailto:envidat@wsl.ch":
        md_metadata_dict["dcat:Dataset"]["dcat:contactPoint"] = [
            individual_contact_point
        ]
    else:
        organization_contact_point = {
            "vcard:Organization": {
                "vcard:fn": "EnviDat Support",
                "vcard:hasEmail": {"@rdf:resource": "mailto:envidat@wsl.ch"},
            }
        }
        md_metadata_dict["dcat:Dataset"]["dcat:contactPoint"] = [
            individual_contact_point,
            organization_contact_point,
        ]

    # theme (MANDATORY)
    md_metadata_dict["dcat:Dataset"]["dcat:theme"] = {
        "@rdf:resource": "http://opendata.swiss/themes/education"
    }

    # language
    md_metadata_dict["dcat:Dataset"]["dct:language"] = {"#text": "en"}

    # keyword
    keywords_list = []
    keywords = get_keywords(metadata_record)
    for keyword in keywords:
        keywords_list += [{"@xml:lang": "en", "#text": keyword}]
    md_metadata_dict["dcat:Dataset"]["dcat:keyword"] = keywords_list

    # Distribution - iterate through package resources and obtain
    # package license (MANDATORY)
    # Call get_distribution_list(metadata_record) to get distibution list
    md_metadata_dict["dcat:Dataset"]["dcat:distribution"] = get_distribution_list(
        metadata_record, package_name
    )

    if as_xml:
        return unparse(md_metadata_dict, short_empty_elements=True, pretty=True)
    return md_metadata_dict


def clean_text(text: str) -> str:
    """Text cleaned of hashes and with modified characters."""
    cleaned_text = (
        text.replace("###", "")
        .replace("##", "")
        .replace(" #", " ")
        .replace("# ", " ")
        .replace("__", "")
        .replace("  ", " ")
        .replace("\r", "\n")
        .replace("\n\n", "\n")
    )
    return cleaned_text


def get_keywords(metadata_record: dict) -> list:
    """Keywords from tags in package (metadata record)."""
    keywords = []
    for tag in metadata_record.get("tags", []):
        name = tag.get("display_name", "").upper()
        keywords += [name]
    return keywords


def get_distribution_list(metadata_record: dict, package_name: str) -> list:
    """Return distribution_list created from package resources list and licence_id."""
    distribution_list = []

    dataset_license = metadata_record.get("license_id", "odc-odbl")

    license_mapping = {
        "wsl-data": (
            "NonCommercialWithPermission-CommercialWithPermission-ReferenceRequired"
        ),
        "odc-odbl": "NonCommercialAllowed-CommercialAllowed-ReferenceRequired",
        "cc-by": "NonCommercialAllowed-CommercialAllowed-ReferenceRequired",
        "cc-by-sa": "NonCommercialAllowed-CommercialAllowed-ReferenceRequired",
        "cc-zero": "NonCommercialAllowed-CommercialAllowed-ReferenceNotRequired",
        "CC0-1.0": "NonCommercialAllowed-CommercialAllowed-ReferenceNotRequired",
    }
    resource_license = license_mapping.get(
        dataset_license,
        "NonCommercialWithPermission-CommercialWithPermission-ReferenceRequired",
    )

    for resource in metadata_record.get("resources", []):
        resource_id = resource.get("id")
        resource_name = resource.get("name", resource_id)
        resource_notes = clean_text(resource.get("description", "No description"))
        resource_page_url = (
            f"https://www.envidat.ch/dataset/{package_name}/resource/"
            + resource.get("id", "")
        )
        resource_url = resource.get("url")

        resource_creation = parse_date(resource["created"]).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        resource_modification = resource_creation
        if resource.get("last_modified", resource.get("metadata_modified", "")):
            resource_modification = parse_date(
                resource.get("last_modified", resource.get("metadata_modified", ""))
            ).strftime("%Y-%m-%dT%H:%M:%SZ")

        resource_size = resource.get("size", False)

        if not resource_size:
            resource_size = 0
            try:
                if len(resource.get("resource_size", "")) > 0:
                    resource_size_obj = json.loads(
                        resource.get("resource_size", "{'size_value': '0'}")
                    )
                    sizes_dict = {
                        "KB": 1024,
                        "MB": 1048576,
                        "GB": 1073741824,
                        "TB": 1099511627776,
                    }
                    resource_size_str = resource_size_obj.get("size_value", "")
                    if len(resource_size_str) > 0:
                        resource_size = (
                            float(resource_size_obj.get("size_value", "0"))
                            * sizes_dict[
                                resource_size_obj.get("size_units", "KB").upper()
                            ]
                        )
            except Exception as e:
                log.error(
                    "resource {} unparseable resource_size: {}".format(
                        resource_url, resource.get("resource_size")
                    )
                )
                log.error(e)
                resource_size = 0

        resource_mimetype = resource.get("mimetype", "")
        if not resource_mimetype or len(resource_mimetype) == 0:
            resource_mimetype = resource.get("mimetype_inner")

        resource_format = resource.get("format")

        distribution = {
            "dcat:Distribution": {
                "@rdf:about": resource_page_url,
                "dct:identifier": metadata_record["name"] + "." + resource_id,
                "dct:title": {"@xml:lang": "en", "#text": resource_name},
                "dct:description": {"@xml:lang": "en", "#text": resource_notes},
                "dct:issued": {
                    "@rdf:datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "#text": resource_creation,
                },
                "dct:modified": {
                    "@rdf:datatype": "http://www.w3.org/2001/XMLSchema#dateTime",
                    "#text": resource_modification,
                },
                "dct:language": "en",
                "dcat:accessURL": {
                    "@rdf:resource": resource_page_url,
                },
                "dct:rights": resource_license,
                "dcat:byteSize": resource_size,
            }
        }
        # mediaType
        if resource_mimetype:
            distribution["dcat:Distribution"]["dcat:mediaType"] = resource_mimetype

        # format
        if resource_format:
            distribution["dcat:Distribution"]["dct:format"] = resource_format

        distribution_list += [distribution]

    return distribution_list


def wrap_packages_dcat_ap_xml(dcat_xml_packages: list) -> str:
    """Add required DCAT-AP catalog XML tags for full DCAT-AP XML.

    Args:
        dcat_xml_packages (list[str,dict]): All DCAT-AP formatted packages to include.
            In string XML or dictionary format.

    Note:
        This is a required final step for producing a DCAT-AP CH format XML.
    """
    catalog_dict = OrderedDict()

    # header
    catalog_dict["@xmlns:dct"] = "http://purl.org/dc/terms/"
    catalog_dict["@xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
    catalog_dict["@xmlns:dcat"] = "http://www.w3.org/ns/dcat#"
    catalog_dict["@xmlns:foaf"] = "http://xmlns.com/foaf/0.1/"
    catalog_dict["@xmlns:xsd"] = "http://www.w3.org/2001/XMLSchema#"
    catalog_dict["@xmlns:rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
    catalog_dict["@xmlns:rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    catalog_dict["@xmlns:vcard"] = "http://www.w3.org/2006/vcard/ns#"
    catalog_dict["@xmlns:odrs"] = "http://schema.theodi.org/odrs#"
    catalog_dict["@xmlns:schema"] = "http://schema.org/"

    if isinstance(dcat_xml_packages, dict):
        packages_dict_list = dcat_xml_packages
    elif isinstance(dcat_xml_packages, str):
        packages_dict_list = parse(dcat_xml_packages)
    elif isinstance(dcat_xml_packages, list):
        if isinstance(dcat_xml_packages[0], dict):
            packages_dict_list = dcat_xml_packages
        elif isinstance(dcat_xml_packages[0], str):
            packages_dict_list = [parse(package) for package in dcat_xml_packages]
    else:
        log.error("Packages in incorrect format. Must be string XML or dict.")
        raise ValueError("Packages in incorrect format. Must be string XML or dict.")
    catalog_dict["dcat:Catalog"] = {"dcat:dataset": packages_dict_list}

    # Assign dcat_catalog_dict dictionary for root element in XML file
    dcat_catalog_dict = OrderedDict()
    dcat_catalog_dict["rdf:RDF"] = catalog_dict

    return unparse(dcat_catalog_dict, short_empty_elements=True, pretty=True)
