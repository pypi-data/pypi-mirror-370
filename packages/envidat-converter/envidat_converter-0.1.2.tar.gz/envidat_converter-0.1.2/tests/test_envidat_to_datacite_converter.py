import unittest
import re
import json

from parameterized import parameterized

from converters.logic.converter_logic.envidat_to_datacite import EnviDatToDataCite

if __name__ == "__main__":
    unittest.main()


class TestDataciteConverterUnit(unittest.TestCase):
    maxDiff = None

    @parameterized.expand(
        [
            (
                "./mock_data/mock_envidat_labes.json",
                "./mock_data/mock_datacite_converter_labes.xml",
            ),
            (
                "./mock_data/mock_envidat_madeup.json",
                "./mock_data/mock_datacite_converter_madeup.xml",
            ),
        ]
    )
    def test_datacite_converter_with_mocked_data(self, mock_file, expected_file):
        # Note: had to remove whitespaces to make test more reliable

        # With
        with open(mock_file, encoding="utf-8") as f:
            mock_data = json.loads(f.read())

        # When
        result = str(EnviDatToDataCite(mock_data))

        result = re.sub(r"\s+", "", result)

        # Then
        with open(expected_file, encoding="utf-8") as f:
            expected_result = f.read()
        expected_result = re.sub(r"\s+", "", expected_result)
        self.assertEqual(result, expected_result)
