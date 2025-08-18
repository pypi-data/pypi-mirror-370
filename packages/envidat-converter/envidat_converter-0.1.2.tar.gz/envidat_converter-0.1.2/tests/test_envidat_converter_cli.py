from unittest.mock import patch, mock_open
from click.testing import CliRunner

from converters.envidat_converter_cli import get_data, convert
from converters.logic.constants import EnviDatConverter, InputTypes

runner = CliRunner()


@patch("converters.envidat_converter_cli.get_inputtype", return_value=InputTypes.DOI)
@patch(
    "converters.envidat_converter_cli.ckan_package_search_doi",
    return_value={"id": "123", "title": "Test Dataset"},
)
def test_get_data_stdout(mock_search, mock_inputtype):
    result = runner.invoke(get_data, ["10.16904/envidat.123"])
    assert result.exit_code == 0
    assert "Test Dataset" in result.output
    mock_search.assert_called_once()


@patch("converters.envidat_converter_cli.get_inputtype", return_value=InputTypes.ID)
@patch(
    "converters.envidat_converter_cli.ckan_package_show",
    return_value={"id": "456", "title": "Test ID Dataset"},
)
@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_get_data_download(mock_makedirs, mock_open_fn, mock_show, mock_inputtype):
    result = runner.invoke(
        get_data, ["dataset-id-456", "--download", "--outputdir", "test_output"]
    )
    assert result.exit_code == 0
    mock_show.assert_called_once()
    mock_open_fn.assert_called_once()
    assert "Result saved to" in result.output


@patch("converters.envidat_converter_cli.get_inputtype", return_value=InputTypes.DOI)
@patch(
    "converters.envidat_converter_cli.converter_logic",
    return_value="<xml>converted</xml>",
)
def test_convert_stdout(mock_converter_logic, mock_inputtype):
    result = runner.invoke(convert, ["10.16904/envidat.123", "--converter", "datacite"])
    assert result.exit_code == 0
    assert "<xml>converted</xml>" in result.output
    mock_converter_logic.assert_called_once_with(
        EnviDatConverter.DATACITE, InputTypes.DOI, "10.16904/envidat.123", False, "prod"
    )


@patch("converters.envidat_converter_cli.get_inputtype", return_value=InputTypes.DOI)
@patch(
    "converters.envidat_converter_cli.converter_logic",
    return_value="<xml>converted</xml>",
)
@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_convert_download(
    mock_makedirs, mock_open_fn, mock_converter_logic, mock_inputtype
):
    result = runner.invoke(
        convert,
        [
            "10.16904/envidat.123",
            "--converter",
            "datacite",
            "--download",
            "--outputdir",
            "test_output",
        ],
    )
    assert result.exit_code == 0
    assert "Result saved to" in result.output
    mock_open_fn.assert_called_once()


@patch(
    "converters.envidat_converter_cli.get_inputtype", side_effect=Exception("Bad input")
)
def test_get_data_error(mock_inputtype):
    result = runner.invoke(get_data, ["invalid-query"])
    assert result.exit_code == 0
    assert "Error: Bad input" in result.output
