"""
Helper methods for affiliation conversion.
"""


def _affiliation_to_dc(self, affiliation) -> dict[str, str]:
    """Returns affiliation in DataCite "affiliation" tag format.

    Uses config to map commonly used affiliations in EnviDat packages
    (i.e. "WSL", "SLF") with long names of institutions
    and ROR identifiers when available.
    """

    # Get affiliation config
    aff_config = self.config[self.affiliation_tag]

    # Strip whitespace from affiliation
    aff = affiliation.strip()

    # Return org dictionary if it exists in config
    aff_key = self.aff_keys.get(aff, "")
    org = aff_config.get(aff_key, {})
    if org:
        # If "affiliationIdentifier" exists then "affiliationIdentifierScheme" REQUIRED
        # DataCite attribute
        if (
            self.affiliation_identifier_tag in org
            and self.affiliation_identifier_scheme_tag not in org
        ):
            return {self.text_tag: aff}
        else:
            return org

    # Else return only affiliation
    return {self.text_tag: aff}
