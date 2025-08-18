import json
from pprint import pprint

from ckan_helper import ckan_package_show


def get_signposting_linktree(package_name):
    pckg = ckan_package_show(package_name)

    linkset = {}

    ls_anchor = f"https://envidat.ch/#/metadata/{package_name}/"
    linkset["anchor"] = ls_anchor
    ls_authors = []
    for author in json.loads(pckg["author"]):
        if "identifier" in author:
            ls_authors.append({"href": f"https://orcid.org/{author['identifier']}"})
    linkset["authors"] = ls_authors

    ls_cite_as = f"https://doi.org/{pckg['doi']}"
    linkset["cite_as"] = ls_cite_as

    ls_described_by = []
    converter_base_url = f"https://www.envidat.ch/api/envidat-converter/convert?query={package_name}&converter="
    converters = ["jsonld", "ris", "dif", "iso", "bibtex", "dcat-ap"]
    type = {
        "jsonld": "application/ld+json",
        "ris": "application/ris",
        "bibtex": "application/bibtex",
        "dif": "application/dif+xml",
        "iso": "application/iso+xml",
        "dcat-ap": "application/dcat+xml",
    }
    for converter in converters:
        ls_described_by.append(
            {"href": converter_base_url + converter, "type": type[converter]}
        )
    linkset["described_by"] = ls_described_by

    ls_items = []
    for item in pckg["resources"]:
        type = item.get("mimetype")
        if type is None:
            type = "text/html"
        ls_items.append({"href": item["url"], "type": type})
    linkset["item"] = ls_items

    ls_license = pckg["license_url"]
    linkset["license"] = ls_license

    ls_type = [
        {"href": "https://schema.org/AboutPage"},
        {"href": "https://schema.org/Dataset"},
    ]
    linkset["type"] = ls_type

    pprint(linkset)

    return linkset
