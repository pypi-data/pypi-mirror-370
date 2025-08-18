from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import status

from converters.api.main import app
from converters.logic.constants import InputTypes

client = TestClient(app)

packages = {"id": "123", "title": "Sample Dataset"}
converted_xml = "<xml>converted</xml>"

"""
Tests for get-data endpoint
"""


@patch(
    "converters.api.envidat_converter_api.get_inputtype", return_value=InputTypes.DOI
)
@patch(
    "converters.api.envidat_converter_api.ckan_package_search_doi",
    return_value=packages,
)
def test_get_data_with_doi(mock_search, mock_inputtype):
    response = client.get(
        "/envidat-converter/get-data", params={"query": "10.16904/envidat.423"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == packages


@patch("converters.api.envidat_converter_api.get_inputtype", return_value=InputTypes.ID)
@patch("converters.api.envidat_converter_api.ckan_package_show", return_value=packages)
def test_get_data_with_id(mock_show, mock_inputtype):
    response = client.get(
        "/envidat-converter/get-data",
        params={"query": "64c2ac8a-5ab9-41bf-89b7-b838d3725966"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == packages


@patch(
    "converters.api.envidat_converter_api.get_inputtype",
    side_effect=Exception("Invalid input"),
)
def test_get_data_invalid(mock_inputtype):
    response = client.get("/envidat-converter/get-data", params={"query": "bad-input"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Error: Invalid input" in response.json()["detail"]


# ---- GET /convert ----


@patch(
    "converters.api.envidat_converter_api.get_inputtype", return_value=InputTypes.DOI
)
@patch(
    "converters.api.envidat_converter_api.converter_logic", return_value=converted_xml
)
def test_convert_to_xml(mock_convert, mock_inputtype):
    response = client.get(
        "/envidat-converter/convert",
        params={"query": "10.16904/envidat.423", "converter": "datacite"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "application/xml"
    assert response.text == converted_xml


@patch(
    "converters.api.envidat_converter_api.get_inputtype", return_value=InputTypes.DOI
)
@patch(
    "converters.api.envidat_converter_api.converter_logic",
    return_value={"json": "converted"},
)
def test_convert_to_json(mock_convert, mock_inputtype):
    response = client.get(
        "/envidat-converter/convert",
        params={"query": "10.16904/envidat.423", "converter": "jsonld"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] != "application/xml"
    assert response.json() == {"json": "converted"}


@patch(
    "converters.api.envidat_converter_api.get_inputtype",
    side_effect=Exception("Bad input"),
)
def test_convert_invalid(mock_inputtype):
    response = client.get(
        "/envidat-converter/convert",
        params={"query": "bad", "converter": "datacite"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Error: Bad input" in response.json()["detail"]
