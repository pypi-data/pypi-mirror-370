import unittest
import json

from parameterized import parameterized
from converters.logic.converter_logic.envidat_to_signposting import EnviDatToSignposting

if __name__ == "__main__":
    unittest.main()


class TestSignpostingConverterUnit(unittest.TestCase):
    maxDiff = None

    @parameterized.expand(
        [
            (
                "./mock_data/mock_envidat_labes.json",
                "./mock_data/mock_signposting_converter_labes.json",
            ),
            (
                "./mock_data/mock_envidat_madeup.json",
                "./mock_data/mock_signposting_converter_madeup.json",
            ),
            (
                "./mock_data/mock_envidat_madeup_minimal_info.json",
                "./mock_data/mock_signposting_converter_madeup_minimal_info.json",
            ),
        ]
    )
    def test_signposting_converter_with_mocked_data(self, mock_file, expected_file):
        # With
        with open(mock_file, encoding="utf-8") as f:
            mock_data = json.loads(f.read())

        # When
        result = json.loads(EnviDatToSignposting(mock_data).to_json_str())

        # Then
        with open(expected_file, encoding="utf-8") as f:
            expected_result = f.read()

        self.assertDictEqual(result, json.loads(expected_result))
