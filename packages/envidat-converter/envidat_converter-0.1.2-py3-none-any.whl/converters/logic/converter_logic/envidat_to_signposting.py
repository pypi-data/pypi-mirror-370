import json

from converters.logic.converter_logic.encoding_helper import encoding_format_helper


class EnviDatToSignposting:
    # TAGS
    anchor_tag = "anchor"
    href_tag = "href"
    authors_tag = "authors"
    cite_as_tag = "cite_as"
    described_by_tag = "described_by"
    item_tag = "item"
    type_tag = "type"
    license_tag = "license"
    text_html_tag = "text/html"

    about_page_url = "https://schema.org/AboutPage"
    dataset_url = "https://schema.org/Dataset"

    appl_ld_json_tag = "application/ld+json"
    appl_ris_tag = "application/ris"
    appl_dif_xml_tag = "application/dif+xml"
    appl_iso_xml_tag = "application/iso+xml"
    appl_bibtex_tag = "application/bibtex"
    appl_dcat_xml_tag = "application/dcat+xml"

    # ALL CONVERTERS NEED TO ADDED HERE
    converters = ["jsonld", "ris", "dif", "iso", "bibtex", "dcat-ap", "datacite"]
    type = {
        "jsonld": "application/ld+json",
        "ris": "application/ris",
        "bibtex": "application/bibtex",
        "dif": "application/dif+xml",
        "iso": "application/iso+xml",
        "dcat-ap": "application/dcat+xml",
        "datacite": "application/datacite+xml",
    }
    converter_base_url = (
        "https://envidat.ch/converters-api-v2/envidat-converter/convert?query="
    )

    def __init__(self, dataset: dict):
        self.sgnpst = {
            self.anchor_tag: f"https://envidat.ch/#/metadata/{dataset['name']}",
            self.authors_tag: self._handle_authors(dataset.get("author", [])),
            self.cite_as_tag: f"https://doi.org/{dataset['doi']}",
            self.described_by_tag: self._handle_described_by(dataset["name"]),
            self.item_tag: self._handle_item(dataset["resources"]),
            self.license_tag: dataset.get("license_url", ""),
            self.type_tag: [
                {self.href_tag: self.about_page_url},
                {self.href_tag: self.dataset_url},
            ],
        }
        self.sgnpst = {k: v for k, v in self.sgnpst.items() if v != "" and v != []}

    def to_json_str(self):
        return json.dumps(self.sgnpst, indent=4)

    def get(self):
        return self.sgnpst

    def _handle_authors(self, authors):
        authors = json.loads(authors)
        sgnpst_authors = []
        for author in authors:
            if "identifier" in author and author["identifier"] != "":
                sgnpst_authors.append(
                    {self.href_tag: f"https://orcid.org/{author['identifier']}"}
                )
        return sgnpst_authors

    def _handle_described_by(self, name):
        sgnpst_described_by = []
        for converter in self.converters:
            sgnpst_described_by.append(
                {
                    self.href_tag: self.converter_base_url
                    + name
                    + "&converter="
                    + converter,
                    self.type_tag: self.type[converter],
                }
            )
        return sgnpst_described_by

    def _handle_item(self, items):
        sgnpst_items = []
        for item in items:
            type = encoding_format_helper(item)
            if type == "No Info":
                type = "text/html"

            sgnpst_items.append({self.href_tag: item["url"], self.type_tag: type})
        return sgnpst_items
