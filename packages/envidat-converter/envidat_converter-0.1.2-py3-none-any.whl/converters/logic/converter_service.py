"""Service that directs the data to the converters."""

from converters.logic.ckan_helper.ckan_helper import (
    ckan_package_show,
    ckan_package_search_doi,
)
from converters.logic.constants import EnviDatConverter, InputTypes
from converters.logic.converter_logic.envidat_to_jsonld import EnviDatToJsonLD
from converters.logic.converter_logic.envidat_to_datacite import EnviDatToDataCite
from converters.logic.converter_logic.envidat_to_signposting import EnviDatToSignposting
from converters.logic.converter_logic.old_converters.bibtex_converter import (
    convert_bibtex,
)
from converters.logic.converter_logic.old_converters.dcat_ap_converter import (
    convert_dcat_ap,
)
from converters.logic.converter_logic.old_converters.dif_converter import convert_dif
from converters.logic.converter_logic.old_converters.iso_converter import convert_iso
from converters.logic.converter_logic.old_converters.ris_converter import convert_ris
from converters.logic.exceptions import (
    TypeNotFoundException,
    ConverterNotFoundException,
)


def converter_logic(converter, type, query, api, environment="prod"):
    """Logic that directs the data to the converters."""

    # Get package
    if type == InputTypes.DOI:
        package = ckan_package_search_doi(query, environment)
    elif type == InputTypes.ID:
        package = ckan_package_show(query, environment)
    else:
        raise TypeNotFoundException(type)

    # Convert package to specified format
    try:
        match converter:
            case EnviDatConverter.DATACITE:
                datacite_instance = EnviDatToDataCite(package)
                return str(datacite_instance)

            case EnviDatConverter.JSONLD:
                jsonld = EnviDatToJsonLD(package)
                if api:
                    return jsonld.get()
                return jsonld.to_json_str()

            case EnviDatConverter.RIS:
                ris = convert_ris(package)
                if api:
                    return str(ris)
                return "\n".join(ris)

            case EnviDatConverter.DIF:
                dif = convert_dif(package)
                return dif

            case EnviDatConverter.ISO:
                iso = convert_iso(package)
                return iso

            case EnviDatConverter.BIBTEX:
                bib = convert_bibtex(package)
                return bib

            case EnviDatConverter.DCATAP:
                dcat = convert_dcat_ap(package)
                return dcat

            case EnviDatConverter.SIGNPOSTING:
                signposting = EnviDatToSignposting(package)
                if api:
                    return signposting.get()
                return signposting.to_json_str()

            # Default case in case none of the converters exist.
            case _:
                raise ConverterNotFoundException(converter)

    except Exception as e:
        raise e
