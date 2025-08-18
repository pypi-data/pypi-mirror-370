"""
Helper methods for format conversion.
"""

from converters.logic.converter_logic.encoding_helper import encoding_format_helper


def _get_dc_formats(self, resources) -> list[dict[str, str]]:
    """Returns resources formats in DataCite "formats" tag format."""
    dc_formats = []

    for resource in resources:
        resource_format = encoding_format_helper(resource)

        dc_format = {self.text_tag: resource_format}
        dc_formats += [dc_format]

    return dc_formats
