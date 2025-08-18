import pytest
from unittest.mock import MagicMock

from converters.logic.converter_service import converter_logic
from converters.logic.constants import EnviDatConverter, InputTypes
from converters.logic.exceptions import (
    TypeNotFoundException,
    ConverterNotFoundException,
)


@pytest.mark.parametrize(
    "converter,expected_callable,input_type,expected_package_func",
    [
        (
            EnviDatConverter.DATACITE,
            "EnviDatToDataCite",
            InputTypes.DOI,
            "ckan_package_search_doi",
        ),
        (
            EnviDatConverter.JSONLD,
            "EnviDatToJsonLD",
            InputTypes.ID,
            "ckan_package_show",
        ),
        (EnviDatConverter.BIBTEX, "convert_bibtex", InputTypes.ID, "ckan_package_show"),
        (EnviDatConverter.DIF, "convert_dif", InputTypes.ID, "ckan_package_show"),
        (EnviDatConverter.ISO, "convert_iso", InputTypes.ID, "ckan_package_show"),
        (
            EnviDatConverter.DCATAP,
            "convert_dcat_ap",
            InputTypes.ID,
            "ckan_package_show",
        ),
        (
            EnviDatConverter.RIS,
            "convert_ris",
            InputTypes.DOI,
            "ckan_package_search_doi",
        ),
    ],
)
def test_converter_logic_calls_correct_converter(
    monkeypatch, converter, expected_callable, input_type, expected_package_func
):
    sample_package = {"id": "123"}

    # Patch package fetchers
    mock_package_func = MagicMock(return_value=sample_package)
    monkeypatch.setattr(
        f"converters.logic.converter_service.{expected_package_func}", mock_package_func
    )

    # Patch converter
    if expected_callable in ["EnviDatToDataCite", "EnviDatToJsonLD"]:
        mock_converter = MagicMock()
        mock_converter_instance = MagicMock()
        if converter == EnviDatConverter.JSONLD:
            mock_converter_instance.get.return_value = {"jsonld": "ok"}
        else:
            mock_converter_instance.__str__.return_value = "<xml>converted</xml>"
        mock_converter.return_value = mock_converter_instance
    else:
        mock_converter = MagicMock(return_value=f"{expected_callable}_called")

    monkeypatch.setattr(
        f"converters.logic.converter_service.{expected_callable}", mock_converter
    )

    # Run the function
    result = converter_logic(converter, input_type, "fake-query", api=True)

    # Assertions
    mock_package_func.assert_called_once_with("fake-query", "prod")
    mock_converter.assert_called_once_with(sample_package)

    if converter == EnviDatConverter.JSONLD:
        assert result == {"jsonld": "ok"}
    elif converter == EnviDatConverter.DATACITE:
        assert result == "<xml>converted</xml>"
    else:
        assert result == f"{expected_callable}_called"


def test_converter_logic_invalid_input_type():
    with pytest.raises(TypeNotFoundException):
        converter_logic(EnviDatConverter.DATACITE, "bad_type", "query", api=True)


def test_converter_logic_unknown_converter(monkeypatch):
    monkeypatch.setattr(
        "converters.logic.converter_service.ckan_package_show", lambda q, e: {}
    )
    with pytest.raises(ConverterNotFoundException):
        converter_logic("not_a_converter", InputTypes.ID, "query", api=True)
