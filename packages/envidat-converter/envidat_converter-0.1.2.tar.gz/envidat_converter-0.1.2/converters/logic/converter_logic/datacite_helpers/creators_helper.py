"""
Helper methods for creator conversion.
"""

from converters.logic.converter_logic.datacite_helpers.affilation_helper import (
    _affiliation_to_dc,
)


def _dc_creator(self, creator: dict):
    dc_creator = {}
    creator_family_name = creator.get(
        self.config[self.creator_tag][self.family_name_tag], ""
    ).strip()
    creator_given_name = creator.get(
        self.config[self.creator_tag][self.given_name_tag], ""
    ).strip()
    if creator_given_name and creator_family_name:
        dc_creator[self.creator_name_tag] = (
            f"{creator_family_name}, {creator_given_name}"
        )
        dc_creator[self.given_name_tag] = creator_given_name
        dc_creator[self.family_name_tag] = creator_family_name
    elif creator_family_name:
        dc_creator[self.creator_name_tag] = creator_family_name

    creator_identifier = creator.get(
        self.config[self.creator_tag][self.name_identifier_tag], ""
    )
    if creator_identifier:
        dc_creator[self.name_identifier_tag] = {
            self.text_tag: creator_identifier.strip(),
            self.nameIdentifierScheme_tag: self.orcid_uppercase,
            self.schemeURI_tag: self.orcid_url,
        }

    affiliations = []
    affiliation = creator.get(self.config[self.creator_tag][self.affiliation_tag], "")
    if affiliation:
        aff = _affiliation_to_dc(self, affiliation)
        if aff:
            affiliations += [aff]

    affiliation_02 = creator.get(f"{self.affiliation_tag}_02", "")
    if affiliation_02:
        aff_02 = _affiliation_to_dc(self, affiliation_02)
        if aff_02:
            affiliations += [aff_02]

    affiliation_03 = creator.get(f"{self.affiliation_tag}_03", "")
    if affiliation_03:
        aff_03 = _affiliation_to_dc(self, affiliation_03)
        if aff_03:
            affiliations += [aff_03]

    if affiliations:
        dc_creator[self.affiliation_tag] = affiliations

    return dc_creator
