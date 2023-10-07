from pyfinnotech.tests.helper import ApiClientTestCase
from pyfinnotech.tests.mock_api_server import (
    valid_mock_ibans,
    valid_mock_facility_sms_tokens,
)
from pyfinnotech.token import FacilitySmsAccessTokenToken

client_invalid_mock_ibans = [
    {},
    "TR910800005000115426432001",
]


class IbanValidationTestCase(ApiClientTestCase):
    def test_national_id_verification(self):
        token = FacilitySmsAccessTokenToken.load(valid_mock_facility_sms_tokens[0])
        result = self.api_client.national_id_verification(
            access_token=token,
            national_id="0067408595",
            birth_date="1365/11/25",
            full_name="سعید غلامی فرد",
            gender="مرد",
        )
        self.assertTrue(result.is_valid)
        self.assertTrue(result.is_alive)
        self.assertTrue(result.is_man)
        self.assertEqual("0067408595", result.national_code)
        self.assertEqual(100, result.full_name_similarity)
