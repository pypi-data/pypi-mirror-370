"""
Helper methods for contributor conversion.
"""

import collections

from converters.logic.converter_logic.datacite_helpers.affilation_helper import (
    _affiliation_to_dc,
)
from converters.logic.converter_logic.datacite_helpers.various_helper import join_tags


def _get_dc_contributor(self, maintainer: dict, config: dict):
    """Returns maintainer in DataCite "contributor" tag format with a
    contributorType of "ContactPerson".

    REQUIRED DataCite attribute for each "contributor": "contributorType",
                                      (value assigned is "Contact Person")

    REQUIRED DataCite property for each "contibutor": "contributorName"

    REQUIRED DataCite property for each "nameIdentifier" property:
                                       "nameIdentifierScheme" (default value is "ORCID")
    """
    dc_contributor = collections.OrderedDict()

    contributor_family_name = maintainer.get(
        config[self.contributor_tag][self.family_name_tag], ""
    ).strip()
    contributor_given_name = maintainer.get(
        config[self.contributor_tag][self.given_name_tag], ""
    ).strip()

    if contributor_given_name:
        dc_contributor[self.contributor_name_tag] = (
            f"{contributor_family_name}, {contributor_given_name}"
        )
        dc_contributor[self.given_name_tag] = contributor_given_name
        dc_contributor[self.family_name_tag] = contributor_family_name
    else:
        dc_contributor[self.contributor_name_tag] = contributor_family_name

    contributor_identifier = maintainer.get(
        config[self.contributor_tag][self.name_identifier_tag], ""
    )
    if contributor_identifier:
        dc_contributor[self.name_identifier_tag] = {
            self.text_tag: contributor_identifier.strip(),
            self.nameIdentifierScheme_tag: maintainer.get(
                join_tags(
                    [
                        self.contributor_tag,
                        self.name_identifier_tag,
                        self.nameIdentifierScheme_tag,
                    ]
                ),
                self.orcid_lowercase,
            ).upper(),
            self.schemeURI_tag: self.orcid_url,
        }

    contributor_affiliation = maintainer.get(
        config[self.contributor_tag][self.affiliation_tag], ""
    )

    if contributor_affiliation:
        affiliation_dc = _affiliation_to_dc(self, contributor_affiliation)
        if affiliation_dc:
            dc_contributor[self.affiliation_tag] = affiliation_dc

    dc_contributor[self.contributor_type_tag] = self.contact_person

    return dc_contributor
