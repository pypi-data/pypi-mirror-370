"""
This converter converts from EnviDat to DataCite version 4.6.

Notes on how this is built:

This class inherits Tags. In Tags we can define tags, but also strings
like URLs, language, etc.
So if there are any changes that need to be done by tags,
go to the Tags class.

This file has 1 class for each metadata. If the class got to bulky
or needed additional helper classes,
it got cut down and moved to the subfolder "datacite_helpers".
You also find the Tags class there.

"""

import collections
import json
import validators

from json import JSONDecodeError
from xmltodict import unparse

from converters.logic.converter_logic.datacite_helpers.tags import Tags
from converters.logic.converter_logic.datacite_helpers.contributor_helper import (
    _get_dc_contributor,
)
from converters.logic.converter_logic.datacite_helpers.creators_helper import (
    _dc_creator,
)
from converters.logic.converter_logic.datacite_helpers.description_helper import (
    _get_dc_descriptions,
)
from converters.logic.converter_logic.datacite_helpers.format_helper import (
    _get_dc_formats,
)
from converters.logic.converter_logic.datacite_helpers.geolocation_helper import (
    _geometrycollection_to_dc_geolocations,
    _get_dc_geolocations,
)
from converters.logic.converter_logic.datacite_helpers.related_items_and_identifiers_helper import (
    get_dc_related_identifiers,
    get_dc_related_identifiers_resources,
)
from converters.logic.converter_logic.datacite_helpers.sizes_helper import _get_sizes


class EnviDatToDataCite(Tags):
    dataset = None

    def __init__(self, dataset: dict):
        self.dataset = dataset

        self.data = collections.OrderedDict()
        self.data[self.xmlns_xsi_tag] = self.schema_instance
        self.data[self.xmlns_tag] = self.namespace
        self.data[self.xsi_schemaLocation_tag] = f"{self.namespace} {self.schema}"

        self._dc_identifier()
        self._dc_creators()
        self._dc_titles()
        self._dc_publisher()  # hardcoded since we always use envidat
        self._dc_publication_year()
        self._dc_resource_type()
        self._dc_subjects()
        self._dc_contributor()
        self._dc_dates()
        self._dc_language()  # hardcoded
        self._dc_alternate_identifiers()
        self._dc_related_identifiers_and_items()
        self._dc_formats()
        self._dc_sizes()
        self._dc_version()
        self._dc_rights()
        self._dc_description()
        self._dc_geolocation()
        self._dc_funding_references()

        self.dc = collections.OrderedDict()
        self.dc[self.resource_tag] = self.data

    def __str__(self):
        return unparse(self.dc, pretty=True)

    def _dc_identifier(self):
        doi = self.dataset[self.config[self.identifier_tag]]
        if doi:
            self.data[self.identifier_tag] = {
                self.text_tag: doi.strip(),
                self.identifierType_tag: self.doi_tag,
            }

    def _dc_creators(self):
        creators = self.dataset[self.config[self.creators_tag]]
        creators = json.loads(creators)
        self.data[self.creators_tag] = {self.creator_tag: []}

        for creator in creators:
            dc_creator = _dc_creator(self, creator)
            self.data[self.creators_tag][self.creator_tag] += [dc_creator]

    def _dc_titles(self):
        title = self.dataset[self.config[self.title_tag]]
        self.data[self.titles_tag] = {self.titles_tag: []}
        self.data[self.titles_tag][self.title_tag] = {
            self.xml_lang_tag: self.english_lang_tag,
            self.text_tag: title,
        }

    def _dc_publisher(self):
        doi = self.dataset[self.config[self.identifier_tag]]
        publication = self.dataset.get(self.publication_tag, {})
        publication = json.loads(publication)
        publisher = publication.get(self.config[self.publisher_tag], self.envidat)

        if doi.startswith("10.16904") or publisher == self.envidat:
            if doi.startswith("10.16904/1000001"):
                self.data[self.publisher_tag] = {
                    self.xml_lang_tag: self.english_lang_tag,
                    self.publisher_identifier_tag: self.default_publisher_identifier,
                    self.publisher_identifier_scheme_tag: self.default_publisher_identifier_scheme,
                    self.schemeURI_tag: self.default_publisher_identifier_uri,
                    self.text_tag: "National Forest Inventory (NFI)",
                }
            else:
                # hardcoded
                self.data[self.publisher_tag] = {
                    self.xml_lang_tag: self.english_lang_tag,
                    self.publisher_identifier_tag: self.default_publisher_identifier,
                    self.publisher_identifier_scheme_tag: self.default_publisher_identifier_scheme,
                    self.schemeURI_tag: self.default_publisher_identifier_uri,
                    self.text_tag: self.envidat,
                }
        else:
            self.data[self.publisher_tag] = {
                self.xml_lang_tag: self.english_lang_tag,
                self.text_tag: publisher.strip(),
            }

    def _dc_publication_year(self):
        publication_info = self.dataset[self.publication_tag]
        tag = self.config[self.publication_year_tag]
        publication_info = json.loads(publication_info)
        self.data[self.publication_year_tag] = publication_info[tag]

    def _dc_resource_type(self):
        self.data[self.resource_type_tag] = {  # hardcoded as well
            self.resource_type_general_tag: self.dataset_uppercase,
            self.text_tag: self.dataset_lowercase,
        }

    def _dc_subjects(self):
        subjects = self.dataset[self.config[self.subjects_tag]]
        self.data[self.subjects_tag] = {self.subject_tag: []}
        for subject in subjects:
            self.data[self.subjects_tag][self.subject_tag] += [
                {
                    self.xml_lang_tag: self.english_lang_tag,
                    self.text_tag: subject[self.config[self.subject_tag]],
                }
            ]

    def _dc_contributor(self):
        self.data[self.contributors_tag] = {self.contributor_tag: []}

        # Get "maintainer" from EnviDat package, assigned as DataCite Contributor "ContactPerson"
        maintainer_dataset = self.dataset.get(self.config[self.contributors_tag], {})
        maintainer = json.loads(maintainer_dataset)

        dc_contributor = _get_dc_contributor(self, maintainer, self.config)
        if dc_contributor:
            self.data[self.contributors_tag][self.contributor_tag] += [dc_contributor]

        # Get "organization" dataset and extract "name" value,
        # assigned as DataCite Contributor "ResearchGroup"
        organization = self.dataset.get(self.organization_tag, {})
        if organization:
            organization_title = organization.get(self.title_tag, "")
            if organization_title:
                dc_research_group = collections.OrderedDict()
                dc_research_group[self.contributor_type_tag] = self.research_group

                dc_research_group[self.contributor_name_tag] = {
                    self.text_tag: organization_title.strip(),
                    self.name_type_tag: self.organizational,
                }
                self.data[self.contributors_tag][self.contributor_tag] += [
                    dc_research_group
                ]

    def _dc_dates(self):
        dates = self.dataset[self.config[self.dates_tag]]
        dc_dates = []
        dates = json.loads(dates)
        for date in dates:
            date_type = date.get(self.config[self.date_type_tag])

            startdate = date.get(self.config[self.date_tag], "")
            enddate = date.get(self.config[self.enddate_tag], "")
            if enddate != "":
                date = f"{startdate}/{enddate}"
            else:
                date = startdate
            dc_date = {self.text_tag: date, self.date_type_tag: date_type.title()}
            dc_dates += [dc_date]

        if dc_dates:
            self.data[self.dates_tag] = {self.date_tag: dc_dates}

    def _dc_language(self):
        self.data[self.language_tag] = self.english_lang_tag

    def _dc_alternate_identifiers(self):
        id = self.dataset[self.id_tag]
        name = self.dataset[self.name_tag]
        alternate_identifiers = []

        name_url = f"{self.envidat_metadata_base_url}{name}"
        alternate_identifiers.append(
            {
                self.text_tag: name_url,
                self.alternate_identifier_type_tag: self.url_uppercase,
            }
        )

        id_url = f"{self.envidat_metadata_base_url}{id}"
        alternate_identifiers.append(
            {
                self.text_tag: id_url,
                self.alternate_identifier_type_tag: self.url_uppercase,
            }
        )

        self.data[self.alternate_identifiers_tag] = {
            self.alternate_identifier_tag: alternate_identifiers
        }

    def _dc_related_identifiers_and_items(self):
        # This is mostly copied from the old converter and only refactored to make it work
        related_datasets = self.dataset.get(self.related_datasets_tag, "")
        dc_related_datasets = get_dc_related_identifiers(
            related_datasets, has_related_datasets=True
        )

        # Get "related_publications" from EnviDat record
        related_publications = self.dataset.get(self.related_publications_tag, "")
        dc_related_publications = get_dc_related_identifiers(related_publications)

        # Get "resources" from EnviDat record,
        # used for DataCite "relatedIdentifiers" and "formats" tags
        dc_resources = get_dc_related_identifiers_resources(
            self.dataset[self.resources]
        )

        # Combine related identifiers from different sources
        related_ids = []
        related_id_sources = [
            dc_related_datasets,
            dc_related_publications,
            dc_resources,
        ]

        # Assign related_ids to sources that are truthy (not empty list)
        for source in related_id_sources:
            if source:
                related_ids += source

        # Assign related_identifier tag(s) to dc
        dc_related_identifiers = collections.OrderedDict()
        if related_ids:
            dc_related_identifiers[self.related_identifier_tag] = related_ids
            self.data[self.related_identifiers_tag] = dc_related_identifiers

            dc_related_items = []

            related_item_data = self.dataset.get(
                self.config.get(self.related_items_tag, []), []
            )
            for related_item in related_item_data:
                # required: title and url
                url = related_item.get(
                    self.config.get(self.related_item_tag).get(self.url_tag, ""), ""
                )
                title = related_item.get(
                    self.config.get(self.related_item_tag).get(self.title_tag, ""), ""
                )
                if url and title:
                    # Check external URL
                    # Currently skipped because we cannot test it as of now and still open questions
                    # size = related_item.get('size') if related_item.get('size') is not None else 0
                    # if not size > 0:
                    #     if not check_external_url(url):
                    #         continue
                    # also some URLS have sizes

                    dc_related_item = collections.OrderedDict()
                    # relatedItemType (is always "Other")
                    related_item_type = self.other
                    dc_related_item[self.related_item_type_tag] = related_item_type

                    # relationType (always references)
                    relation_type = self.references
                    dc_related_item[self.relation_type_tag] = relation_type

                    # relatedItemIdentifier: URL
                    dc_related_item[self.related_item_identifier_tag] = {
                        self.related_item_identifier_type_tag: self.url_uppercase,
                        self.text_tag: url.strip(),
                    }

                    # relatedItem title
                    # since there is only one title per resource we don't handle more than one title even though datacite allows it
                    dc_title = collections.OrderedDict()
                    dc_title[self.title_tag] = title.strip()
                    dc_related_item[self.titles_tag] = dc_title

                    dc_related_items.append(dc_related_item)

            # If related items exist, add them:
            if dc_related_items:
                self.data[self.related_items_tag] = {
                    self.related_item_tag: dc_related_items
                }

    def _dc_formats(self):
        dc_formats = _get_dc_formats(self, self.dataset[self.resources])
        if dc_formats:
            self.data[self.formats_tag] = {self.format_tag: dc_formats}

    def _dc_sizes(self):
        dc_sizes = _get_sizes(self, self.dataset[self.resources])
        if dc_sizes:
            self.data[self.sizes_tag] = {self.size_tag: dc_sizes}

    def _dc_version(self):
        dc_version = self.dataset.get(self.config[self.version_tag], "")
        if not dc_version:
            dc_version = "1"
        self.data[self.version_tag] = {self.text_tag: dc_version}

    def _dc_rights(self):
        # mostly copied over from old converter
        rights = {}
        rights_title = self.dataset.get(self.config[self.rights_tag][self.text_tag], "")
        if rights_title:
            rights = {
                self.xml_lang_tag: self.english_lang_tag,
                self.text_tag: rights_title,
            }

        rights_uri = self.dataset.get(
            self.config[self.rights_tag][self.rights_uri_tag], ""
        )
        if rights_uri:
            rights[self.rights_uri_tag] = rights_uri

        license_id = self.dataset.get(
            self.config[self.rights_tag][self.rights_identifier_tag], "no-license-id"
        )

        if license_id in self.config:
            license_id = self.config[license_id]
            rights[self.schemeURI_tag] = self.default_rights_scheme_uri
            rights[self.rights_identifier_scheme_tag] = self.default_rights_identifier
            rights[self.rights_identifier_tag] = license_id
        if rights:
            self.data[self.rights_list_tag] = {self.rights_tag: [rights]}

    def _dc_description(self):
        notes = self.dataset.get(self.config[self.description_tag], "")
        dc_descriptions = _get_dc_descriptions(
            self,
            notes,
            self.description_type_tag,
            self.xml_lang_tag,
            self.dataset[self.resources],
        )

        self.data[self.descriptions_tag] = {self.description_tag: dc_descriptions}

    def _dc_geolocation(self):
        # GeoLocation
        dc_geolocations = []

        # Get spatial data from dataset
        try:
            spatial = json.loads(
                self.dataset.get(self.config[self.geolocations_tag], "")
            )
            spatial_type = spatial.get(self.type_tag, "").lower()

            if spatial and spatial_type:
                if spatial_type == self.geometry_collection:
                    dc_geolocations = _geometrycollection_to_dc_geolocations(
                        self, spatial
                    )
                else:
                    dc_geolocations = _get_dc_geolocations(self, spatial, spatial_type)
        except JSONDecodeError:
            dc_geolocations = []

        # Assign converted spatial and spatial_info values to corresponding DataCite tags
        if dc_geolocations:
            geolocation_place = self.dataset.get(
                self.config[self.geolocation_place_tag], ""
            )
            if geolocation_place:
                datacite_geolocation_place = {
                    self.geolocation_place_tag: geolocation_place.strip()
                }
                dc_geolocations += [datacite_geolocation_place]

            self.data[self.geolocations_tag] = {self.geolocation_tag: dc_geolocations}

    def _dc_funding_references(self):
        dc_funding_refs = []
        funding = json.loads(
            self.dataset.get(self.config[self.funding_references_tag], [])
        )
        for funder in funding:
            dc_funding_ref = collections.OrderedDict()

            # "funderName" is a REQUIRED DataCite attribute for each "fundingReference"
            funder_name = funder.get(
                self.config[self.funding_reference_tag][self.funder_name_tag], ""
            )
            if funder_name:
                dc_funding_ref[self.funder_name_tag] = funder_name.strip()

                award_number = funder.get(
                    self.config[self.funding_reference_tag][self.award_number_tag], ""
                )

                award_uri = funder.get(
                    self.config[self.funding_reference_tag][self.award_uri_tag], ""
                )

                if award_uri and validators.url(award_uri):
                    if award_number:
                        award = {
                            self.award_uri_tag: award_uri,
                            self.text_tag: award_number.strip(),
                        }
                    else:
                        award = {self.award_uri_tag: award_uri, self.text_tag: ":unav"}
                    dc_funding_ref[self.award_number_tag] = award
                elif award_number:
                    dc_funding_ref[self.award_number_tag] = award_number.strip()

                dc_funding_refs += [dc_funding_ref]

        if dc_funding_refs:
            self.data[self.funding_references_tag] = {
                self.funding_reference_tag: dc_funding_refs
            }
