"""
FastAPI endpoints for the envidat converter.
"""

from typing import Annotated

from fastapi import HTTPException, APIRouter, Query
from fastapi.responses import Response

from converters.logic.ckan_helper.ckan_helper import (
    ckan_package_search_doi,
    ckan_package_show,
)
from converters.logic.constants import EnviDatConverter, InputTypes
from converters.logic.converter_service import converter_logic
from converters.logic.general_helpers import get_inputtype

router = APIRouter(prefix="/envidat-converter", tags=["envidat-converter"])


# Route for retrieving EnviDat metadata
@router.get("/get-data", name="Get EnviDat metadata")
async def get_data(
    query: Annotated[
        str,
        Query(
            alias="query",
            description="Either a DOI or an EnviDat package id or name",
            openapi_examples={
                "package name": {
                    "summary": "EnviDat package name",
                    "value": "data-reliability-study-avalanche-size-and-outlines",
                },
                "package ID": {
                    "summary": "EnviDat package ID",
                    "value": "64c2ac8a-5ab9-41bf-89b7-b838d3725966",
                },
                "DOI on EnviDat": {
                    "summary": "DOI on EnviDat",
                    "value": "10.16904/envidat.423",
                },
            },
        ),
    ],
):
    try:
        inputtype = get_inputtype(query)
        if inputtype == InputTypes.DOI:
            package = ckan_package_search_doi(query)
        else:
            package = ckan_package_show(query)
        return package
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


# Route for converting EnviDat metadata
@router.get("/convert", name="Convert EnviDat dataset to other metadata format")
async def convert(
    query: Annotated[
        str,
        Query(
            alias="query",
            description="Either a DOI or an EnviDat package id or name",
            openapi_examples={
                "package name": {
                    "summary": "EnviDat package name",
                    "value": "data-reliability-study-avalanche-size-and-outlines",
                },
                "package ID": {
                    "summary": "EnviDat package ID",
                    "value": "64c2ac8a-5ab9-41bf-89b7-b838d3725966",
                },
                "DOI on EnviDat": {
                    "summary": "DOI on EnviDat",
                    "value": "10.16904/envidat.423",
                },
            },
        ),
    ],
    converter: EnviDatConverter,
):
    try:
        inputtype = get_inputtype(query)
        result = converter_logic(converter, inputtype, query, True, "prod")
        if converter in [
            EnviDatConverter.DATACITE,
            EnviDatConverter.DIF,
            EnviDatConverter.ISO,
            EnviDatConverter.DCATAP,
        ]:
            return Response(content=result, media_type="application/xml")
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
