"""
Helper methods for description conversion.
"""

from converters.logic.converter_logic.datacite_helpers.sizes_helper import _get_size
from converters.logic.converter_logic.encoding_helper import encoding_format_helper


def _get_dc_descriptions(
    self, notes, dc_description_type_tag, dc_xml_lang_tag, resources
) -> list[str]:
    """Returns notes in DataCite "descriptions" tag format.

    "descriptionType" is a REQUIRED DataCite attribute for each "description",
         (value assigned to "Abstract")

    Logs warning for a description that is less than 100 characters.
    """
    dc_descriptions = []

    if notes:
        description_text = (
            notes.replace("\r", "")
            .replace(">", "-")
            .replace("<", "-")
            .replace("__", "")
            .replace("#", "")
            .replace("\n\n", "\n")
            .replace("\n\n", "\n")
        )

        datacite_description = {
            self.text_tag: description_text.strip(),
            dc_description_type_tag: self.abstract,
            dc_xml_lang_tag: self.english_lang_tag,
        }

        dc_descriptions += [datacite_description]

        if resources:
            for resource in resources:
                dc_descriptions += _description_from_resource(
                    self, dc_description_type_tag, dc_xml_lang_tag, resource
                )

    return dc_descriptions


def _description_from_resource(
    self, dc_description_type_tag, dc_xml_lang_tag, resource
):
    resource_title = resource.get("name", "Not available")
    resource_size = _get_size(self, resource)
    resource_url = resource.get("url", "Not available")
    resource_format = encoding_format_helper(resource)
    resource_description = resource.get("description")

    description_text = f"""
    Resource Title: {resource_title}
    Size: {resource_size}
    Format: {resource_format}
    URL: {resource_url}
    Description: {resource_description}
    """
    description = {
        self.text_tag: description_text.strip(),
        dc_description_type_tag: self.other,
        dc_xml_lang_tag: self.english_lang_tag,
    }
    return [description]
