import unittest
import json

from parameterized import parameterized
from converters.logic.converter_logic.envidat_to_jsonld import EnviDatToJsonLD

if __name__ == "__main__":
    unittest.main()


class TestDataciteConverterUnit(unittest.TestCase):
    maxDiff = None

    @parameterized.expand(
        [
            (
                "./mock_data/mock_envidat_labes.json",
                "./mock_data/mock_jsonld_converter_labes.json",
            ),
            (
                "./mock_data/mock_envidat_madeup.json",
                "./mock_data/mock_jsonld_converter_madeup.json",
            ),
        ]
    )
    def test_datacite_converter_with_mocked_data(self, mock_file, expected_file):
        # With
        with open(mock_file, encoding="utf-8") as f:
            mock_data = json.loads(f.read())

        # When
        result = json.loads(EnviDatToJsonLD(mock_data).to_json_str())

        # Then
        with open(expected_file, encoding="utf-8") as f:
            expected_result = f.read()

        self.assertDictEqual(result, json.loads(expected_result))
