from pyfinnotech.tests.helper import ApiClientTestCase
from pyfinnotech.tests.mock_api_server import valid_mock_cards

client_invalid_mock_cards = [
    "000000000000000",
    "A000000000000000",
]


class CardToIbanTestCase(ApiClientTestCase):
    def test_server_card_to_iban(self):
        for c in valid_mock_cards:
            result = self.api_client.card_to_iban(c)
            self.assertTrue(result.is_valid)
            self.assertIsNotNone(result.iban)
            self.assertIsNotNone(result.bank_name)
            self.assertIsNotNone(result.deposit)
            self.assertIsNotNone(result.card)
            self.assertIsNotNone(result.deposit_status)
            self.assertIsNotNone(result.deposit_description)
            self.assertIsNotNone(result.deposit_comment)
            self.assertIsNotNone(result.deposit_owners)
            self.assertIsNotNone(result.alert_code)

    def test_client_card_to_iban(self):
        for c in client_invalid_mock_cards:
            with self.assertRaises(ValueError):
                self.api_client.card_to_iban(c)
