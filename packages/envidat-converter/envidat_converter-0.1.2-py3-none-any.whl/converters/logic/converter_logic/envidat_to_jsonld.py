"""
This converter converts from EnviDat to JsonLD, based on the Zenodo version.

Opposed to the envidat to datacite converter, this is pretty small and clean, so i kept it as one file.

"""

import json
import xml.etree.ElementTree as ET

from requests import get

from converters.logic.converter_logic.encoding_helper import encoding_format_helper


class EnviDatToJsonLD:
    # TAGS JSON LD
    context_tag = "@context"
    type_tag = "@type"
    id_tag = "@id"
    identifier_tag = "identifier"
    url_tag = "url"
    inLanguage_tag = "inLanguage"
    contentSize_tag = "contentSize"
    size_tag = "size"
    publisher_tag = "publisher"
    name_tag = "name"
    alternateName_tag = "alternateName"
    datePublished_tag = "datePublished"
    creator_tag = "creator"
    author_tag = "author"
    givenName_tag = "givenName"
    familyName_tag = "familyName"
    affiliation_tag = "affiliation"
    keywords_tag = "keywords"
    temporal_tag = "temporal"
    sameAs_tag = "sameAs"
    distribution_tag = "distribution"
    content_url_tag = "contentUrl"
    encoding_format_tag = "encodingFormat"

    units = {
        "kb": 1024,
        "mb": 1024**2,
        "gb": 1024**3,
        "tb": 1024**4,
    }

    dictionary = {
        "name": "title",
        "description": "notes",
        # Note on the dates: Zenodo uses these for TECHNICAL metadata
        "dateCreated": "metadata_created",
        "dateModified": "metadata_modified",
        "version": "version",
        "license": "license_url",
    }

    def __init__(self, dataset: dict):
        self.jld = {
            self.context_tag: "http://schema.org",
            self.type_tag: "https://schema.org/Dataset",
            self.url_tag: f"https://envidat.ch/#/metadata/{dataset['name']}",
            self.id_tag: "https://doi.org/" + dataset["doi"],
            self.identifier_tag: "https://doi.org/" + dataset["doi"],
            self.sameAs_tag: {
                self.type_tag: "Dataset",
                self.id_tag: f"https://envidat.ch/#/metadata/{dataset['id']}",
            },
            # Note: we currently only have english entries and only plan to use english.
            self.inLanguage_tag: {
                self.alternateName_tag: "eng",
                self.type_tag: "Language",
                self.name_tag: "English",
            },
            self.publisher_tag: {
                self.type_tag: "Organization",
                self.name_tag: json.loads(dataset.get("publication")).get("publisher"),
            },
            self.contentSize_tag: self._handle_sizes(dataset.get("resources")),
            self.size_tag: self._handle_sizes(dataset.get("resources")),
            self.datePublished_tag: json.loads(dataset.get("publication")).get(
                "publication_year"
            ),
            self.creator_tag: self._handle_creators(dataset.get("author")),
            self.author_tag: self._handle_creators(dataset.get("author")),
            self.keywords_tag: self._handle_keywords(dataset.get("tags")),
            self.temporal_tag: self._handle_temporal(dataset.get("date")),
            self.distribution_tag: self._handle_distribution(
                dataset.get("resources"), dataset.get("doi")
            ),
        }

        # Note that zenodo does not seem to convert spatial information to json-ld (at this point)

        for key, value in self.dictionary.items():
            entry = dataset.get(value, "")
            if entry:
                self.jld[key] = entry

    def to_json_str(self):
        return json.dumps(self.jld, indent=4)

    def get(self):
        return self.jld

    def _handle_sizes(self, resources):
        total_size = 0

        for resource in resources:
            size = self._size_helper(
                resource.get("size", ""), resource.get("resource_size", "")
            )
            if size:
                total_size += int(size)

        if total_size > self.units["tb"]:
            result = f"{round(total_size / self.units['tb'])} TB"
        elif total_size > self.units["gb"]:
            result = f"{round(total_size / self.units['gb'], 2)} GB"
        elif total_size > self.units["mb"]:
            result = f"{round(total_size / self.units['mb'], 2)} MB"
        elif total_size > self.units["kb"]:
            result = f"{round(total_size / self.units['kb'], 2)} KB"
        else:
            result = f"{total_size} bytes"
        return result

    def _handle_creators(self, authors):
        authors = json.loads(authors)
        creators = []
        for author in authors:
            affiliations = []
            affiliations_list = []
            affiliation_field_names = [
                "affiliation",
                "affiliation_02",
                "affiliation_03",
            ]
            for affiliation_field in affiliation_field_names:
                if author.get(affiliation_field):
                    affiliations_list.append(author.get(affiliation_field))

            for affiliation in affiliations_list:
                affiliations.append(
                    {self.type_tag: "Organization", self.name_tag: affiliation}
                )

            creator = {
                self.type_tag: "Person",
                self.name_tag: f"{author.get('name')}, {author.get('given_name')}",
                self.givenName_tag: author.get("given_name"),
                self.familyName_tag: author.get("name"),
                self.affiliation_tag: affiliations,
            }

            id = author.get("identifier", "")
            if id:
                creator[self.id_tag] = id
            creators.append(creator)
        return creators

    def _handle_keywords(self, keywords):
        keyword_list = [keyword["display_name"] for keyword in keywords]
        return ", ".join(keyword_list)

    def _handle_temporal(self, dates):
        temporal = []
        # in zenodo i only found temporal used for all dates without any info on what is what
        # also, have not found a date range example
        dates = json.loads(dates)
        for date in dates:
            start_date = date.get("date")
            end_date = date.get("end_date", False)

            if start_date and end_date:
                temporal.append(f"{start_date} - {end_date}")
            else:
                temporal.append(f"{start_date}")

        return temporal

    def _handle_distribution(self, resources, doi):
        distrs = []
        if doi.startswith("10.16904"):
            distrs.append(
                {
                    self.type_tag: "DataDownload",
                    self.content_url_tag: f"https://envidat-doi.os.zhdk.cloud.switch.ch/?prefix={doi.replace('/', '_')}",
                    self.name_tag: "All resources in one place",
                }
            )

        for resource in resources:
            # We discussed that the URL should point to the copy in the envidat-doi bucket if it's an S3 bucket.
            # Once this is done we can delete this:
            # vvv
            rs_url = resource.get("url")
            base = f"https://envidat-doi.os.zhdk.cloud.switch.ch/?prefix={doi.replace('/', '_')}"
            if rs_url.startswith("https://os.zhdk.cloud.switch.ch/envicloud"):
                namespace = {"ns": "http://s3.amazonaws.com/doc/2006-03-01/"}
                url = base
                while True:
                    response = get(url, timeout=10)
                    if response.status_code != 200:
                        raise Exception(f"Error fetching data: {response.status_code}")
                    content = response.text
                    root = ET.fromstring(content)

                    for item in root.findall("ns:Contents", namespace):
                        key_element = item.find("ns:Key", namespace).text

                        if key_element.count("/") > 1:
                            parts = key_element.split("/")
                            rs_url = f"{base}/{parts[1]}"
                            break

                    nextMarker = root.find("ns:NextMarker", namespace)
                    if nextMarker is not None:
                        url = f"{base}&marker={nextMarker.text}"
                    else:
                        break
            # ^^^

            distr = {
                self.type_tag: "DataDownload",
                self.content_url_tag: rs_url,
                self.contentSize_tag: self._size_helper(
                    resource.get("size", ""), resource.get("resource_size", "")
                ),
                self.encoding_format_tag: encoding_format_helper(resource),
                self.name_tag: resource.get("name"),
            }

            distrs.append(distr)
        return distrs

    def _size_helper(self, size_value, resource_size_value):
        size = size_value
        if not size:
            size = resource_size_value
            if size:
                size = json.loads(size)
                unit = size.get("size_units", "")
                value = size.get("size_value", "")
                if value and unit:
                    size = float(value) * self.units[unit]
                else:
                    size = 0
            if not size:
                size = 0
        return int(size)
