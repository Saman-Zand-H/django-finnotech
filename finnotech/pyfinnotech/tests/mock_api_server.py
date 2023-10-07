import base64
import functools

from nanohttp import (
    RestController,
    json,
    HttpNotFound,
    context,
    HttpUnauthorized,
    HttpBadRequest,
)

from pyfinnotech.const import ALL_SCOPE_CLIENT_CREDENTIALS

valid_mock_cards = ["0000000000000000"]

valid_mock_ibans = ["IR910800005000115426432001"]

valid_mock_client_id = "mock-app"
valid_mock_client_secret = "mock-secret"

valid_mock_client_credential_tokens = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Im1vY2stYXBwIn0.maxHiBX70CtQM_p_hNsv0RLmfhj_eg7bmRuN6We9HEU"
]

invalid_mock_client_credential_tokens = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInZhbGlkIjpmYWxzZX0.eyJpZCI6Im1vY2stYXBwIn0"
    ".9AxqC62m5tRc9Jxy5Mfj58YpgO2ANfcWhsm6LNMtgpo"
]

valid_mock_client_credential_refresh_tokens = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Im1vY2stYXBwIn0.W1sHpsKjNZrOg73ye0fVllbkzooK6tiIZl6TjiRsUlU"
]

invalid_mock_client_credential_refresh_tokens = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Im1vY2stYXBwIn0.W1sHpsKjNZrOg73ye0fVllbkzooK6tiIZl6TjiRsUlU"
]

valid_mock_facility_sms_tokens = [
    "eyJhbGciOiJIUzI1NiJ9.eyJyZXN1bHQiOnsiY2xpZW50SWQiOiJzbW9rZXkiLCJzY29wZXMiOlsiY3JlZGl0OnNtcy1hZHZhbmNlLXJlbGlhYmlsaXR5OmdldCJdLCJkZXBvc2l0cyI6W10sImxpZmVUaW1lIjoiODY0MDAwMDAwIiwiYmFuayI6IiIsInR5cGUiOiJDT0RFIiwiY3JlYXRpb25EYXRlIjoiMTM5ODA0MTIxMzQ2MDkiLCJ1c2VySWQiOiIwMDEyNjc0MDQ0IiwibWF4QW1vdW50UGVyVHJhbnNhY3Rpb24iOjAsIm1vbnRobHlDYWxsTGltaXRhdGlvbiI6MCwiYXV0aF90eXBlIjoiU01TIiwicmVmcmVzaFRva2VuIjoiUEZDaUxyMTJYWG9XTGx0bmlFM2htcHBFMFRqWWNHY2N0bXJnSkYzWHo5NHhtZDZDM0FDczhIaFpZU25iVU1PZDY3RnFEMkdiQWFkdHZ3OEpZRXdoOGlXaFlTclUwR1lNYzEyYWVXYktkVTA2S1NSaXFManFneWtPZ204WmpOR2ljQjJGMU9ES0VyU3gxcUQzMzZFQTQyYVc5WjBGTkJpSVZuMUpyRFloam8wSFFaQmo0cnFDRTNLaUptcmw2MXNvZnZzalg5MmJWbmV4ZHY1SmFWQURRVzFSY0ZOYzJnSWVJcnloMENxUXBLQmxmUURVcWNweTd1UUl0emtBSGFxaSIsInZhbHVlIjoiZXlKaGJHY2lPaUpTVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR2xsYm5SSlpDSTZJbk50YjJ0bGVTSXNJbk5qYjNCbGN5STZXeUpqY21Wa2FYUTZjMjF6TFdGa2RtRnVZMlV0Y21Wc2FXRmlhV3hwZEhrNloyVjBJbDBzSW1SbGNHOXphWFJ6SWpwYlhTd2liR2xtWlZScGJXVWlPaUk0TmpRd01EQXdNREFpTENKaVlXNXJJam9pSWl3aWRIbHdaU0k2SWtOUFJFVWlMQ0pqY21WaGRHbHZia1JoZEdVaU9pSXhNems0TURReE1qRXpORFl3T1NJc0luVnpaWEpKWkNJNklqQXdNVEkyTnpRd05EUWlMQ0p0WVhoQmJXOTFiblJRWlhKVWNtRnVjMkZqZEdsdmJpSTZNQ3dpYlc5dWRHaHNlVU5oYkd4TWFXMXBkR0YwYVc5dUlqb3dMQ0poZFhSb1gzUjVjR1VpT2lKVFRWTWlMQ0p5WldaeVpYTm9WRzlyWlc0aU9pSlFSa05wVEhJeE1saFliMWRNYkhSdWFVVXphRzF3Y0VVd1ZHcFpZMGRqWTNSdGNtZEtSak5ZZWprMGVHMWtOa016UVVOek9FaG9XbGxUYm1KVlRVOWtOamRHY1VReVIySkJZV1IwZG5jNFNsbEZkMmc0YVZkb1dWTnlWVEJIV1Uxak1USmhaVmRpUzJSVk1EWkxVMUpwY1V4cWNXZDVhMDluYlRoYWFrNUhhV05DTWtZeFQwUkxSWEpUZURGeFJETXpOa1ZCTkRKaFZ6bGFNRVpPUW1sSlZtNHhTbkpFV1docWJ6QklVVnBDYWpSeWNVTkZNMHRwU20xeWJEWXhjMjltZG5OcVdEa3lZbFp1Wlhoa2RqVktZVlpCUkZGWE1WSmpSazVqTW1kSlpVbHllV2d3UTNGUmNFdENiR1pSUkZWeFkzQjVOM1ZSU1hSNmEwRklZWEZwSWl3aWFXRjBJam94TlRZeU1UUTFNelk1ZlEuREZtbmRhSDJDMEtyamRzWFljQkV6eGU0all0Y01xNzJLbmdKWlRQZkpLa1p3aktsdGVUcHVOd2doSEJRMjFpbGZucnJkWklqZEFsUzdNeXlRdjJ4ZFZ3UUJTZ2hsd3dBSEM0ZXpwTkZuV0JqUmRhRXV4WDhnYUhxalRYc1pjd1l2VkY3V09XaFN0RDJsTkVjOHFRQVZOZjFJdnhhUjNONmJTUUEyZkp1V0lvUWpFem5HUi1QSGNDVTdwbktHM0sycGdKOThrMktjUGx4QkI1Z2FNQWI1Rmlrc2FnYnZXWTY5b0tOc3BQSjFJT05PbkMyQVhuZFFuS2hvTDNxWk9BRmFPeXBRYWI4Wkt4UXBqU3R6NTREOEZQOTB5QnREYWFxUGhkdnlXWE1makdiZTZySmkxM3FKcG1VbzktRmUycEFrWENSS0VsbDNIUnhwT0taV213In0sInN0YXR1cyI6IkRPTkUifQ.FRZX9zeWAZZBUrTqPvnoJ4lGLelYYDr4Wsfu80pKiI4"
]


def authorize_client_credential(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "HTTP_AUTHORIZATION" not in context.environ:
            raise HttpUnauthorized()

        encoded_token = context.environ["HTTP_AUTHORIZATION"]
        if encoded_token is None or not encoded_token.strip().strip("Bearer").strip():
            raise HttpUnauthorized()
        encoded_token = encoded_token.strip().strip("Bearer").strip()

        if encoded_token in valid_mock_client_credential_tokens:
            return func(*args, **kwargs)

        if encoded_token in invalid_mock_client_credential_tokens:
            raise HttpUnauthorized()
        raise HttpUnauthorized()

    return wrapper


def authorize_sms_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "HTTP_AUTHORIZATION" not in context.environ:
            raise HttpUnauthorized()

        encoded_token = context.environ["HTTP_AUTHORIZATION"]
        if encoded_token is None or not encoded_token.strip().strip("Bearer").strip():
            raise HttpUnauthorized()
        encoded_token = encoded_token.strip().strip("Bearer").strip()

        if encoded_token in valid_mock_facility_sms_tokens:
            return func(*args, **kwargs)

        raise HttpUnauthorized()

    return wrapper


def authorize_basic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "HTTP_AUTHORIZATION" not in context.environ:
            raise HttpUnauthorized()

        encoded_token = context.environ["HTTP_AUTHORIZATION"]
        if encoded_token is None or not encoded_token.strip().strip("Basic").strip():
            raise HttpUnauthorized()
        encoded_token = encoded_token.strip().strip("Basic").strip()

        try:
            credential = base64.decodebytes(encoded_token.encode()).decode().split(":")
            if (
                credential[0] == valid_mock_client_id
                and credential[1] == valid_mock_client_secret
            ):
                return func(*args, **kwargs)
        except:
            raise HttpUnauthorized()

        raise HttpUnauthorized()

    return wrapper


class MockOauthController(RestController):
    @json
    @authorize_basic
    def post(self, r1: str = None):
        if r1 == "token":
            return {
                "result": {
                    "value": valid_mock_client_credential_tokens[0],
                    "scopes": [",".join(ALL_SCOPE_CLIENT_CREDENTIALS)],
                    "lifeTime": 864000000,
                    "creationDate": "13970730111355",
                    "refreshToken": valid_mock_client_credential_refresh_tokens,
                },
                "status": "DONE",
            }


class MockCardController(RestController):
    @json
    @authorize_client_credential
    def get(self, card_number: str = None):
        if card_number in valid_mock_cards:
            return {
                "result": {
                    "destCard": "xxxx-xxxx-xxxx-3899",
                    "name": "علی آقایی",
                    "result": "0",
                    "description": "موفق",
                    "doTime": "1396/06/15 12:32:04",
                },
                "status": "DONE",
                "trackId": "get-cardInfo-0232",
            }

        raise HttpBadRequest()


class MockIbanController(RestController):
    @json
    @authorize_client_credential
    def get(self):
        iban = context.query_string.get("iban")
        if iban in valid_mock_ibans:
            return {
                "trackId": "get-iban-inquiry-029",
                "result": {
                    "IBAN": "IR910800005000115426432001",
                    "bankName": "قرض الحسنه رسالت",
                    "deposit": "10.6423499.1",
                    "depositDescription": "حساب فعال است",
                    "depositComment": "سپرده حقيقي قرض الحسنه پس انداز حقيقي ريالی شیما کیایی",
                    "depositOwners": [{"firstName": "شیما", "lastName": "کیایی"}],
                    "depositStatus": "02",
                    "errorDescription": "بدون خطا",
                },
                "status": "DONE",
            }

        raise HttpBadRequest()


class MockCardToIbanController(RestController):
    @json
    @authorize_client_credential
    def get(self):
        card = context.query_string.get("card")
        if card in valid_mock_cards:
            return {
                "trackId": "cardToIban-029",
                "result": {
                    "IBAN": "IR910800005000115426432001",
                    "bankName": "قرض الحسنه رسالت",
                    "deposit": "10.6423499.1",
                    "card": "6362141081734437",
                    "depositStatus": "02",
                    "depositDescription": "حساب فعال است",
                    "depositComment": "سپرده حقيقي قرض الحسنه پس انداز حقيقي ريالی شیما کیایی",
                    "depositOwners": [{"firstName": "شیما", "lastName": "کیایی"}],
                    "alertCode": "01",
                },
                "status": "DONE",
            }

        raise HttpBadRequest()


class MockNationalIdVerification(RestController):
    @json
    @authorize_sms_token
    def get(self):
        return {
            "result": {
                "nationalCode": "0067408595",
                "birthDate": "1365/11/25",
                "status": "DONE",
                "fullName": "سعید غلامی فرد",
                "firstName": "سعید",
                "lastName": "غلامی فرد",
                "fatherName": "علی",
                "gender": "مرد",
                "deathStatus": "زنده",
                "fullNameSimilarity": 100,
                "firstNameSimilarity": 100,
                "lastNameSimilarity": 100,
                "fatherNameSimilarity": 100,
                "genderSimilarity": 100,
                "description": "",
            },
            "status": "DONE",
            "trackId": "nid-inq-9602281200",
        }


class FinnotechRootMockController(RestController):
    cards = MockCardController()
    ibanInquiry = MockIbanController()
    oauth2 = MockOauthController()
    nidVerification = MockNationalIdVerification()
    cardToIban = MockCardToIbanController()

    def __call__(self, *remaining_paths):
        if remaining_paths[0] == "oak":
            if remaining_paths[1] == "v2":
                if remaining_paths[2] == "clients":
                    from pyfinnotech.tests.helper import valid_mock_client_id

                    if remaining_paths[3] == valid_mock_client_id:
                        if remaining_paths[4] in ["ibanInquiry"]:
                            return super().__call__(*remaining_paths[4:])

        elif remaining_paths[0] == "mpg":
            if remaining_paths[1] == "v2":
                if remaining_paths[2] == "clients":
                    from pyfinnotech.tests.helper import valid_mock_client_id

                    if remaining_paths[3] == valid_mock_client_id:
                        if remaining_paths[4] in ["cards"]:
                            return super().__call__(*remaining_paths[4:])

        elif remaining_paths[0] == "dev":
            if remaining_paths[1] == "v2":
                if remaining_paths[2] == "oauth2":
                    return super().__call__(*remaining_paths[2:])

        elif remaining_paths[0] == "facility":
            if remaining_paths[1] == "v2":
                if remaining_paths[2] == "clients":
                    from pyfinnotech.tests.helper import valid_mock_client_id

                    if remaining_paths[3] == valid_mock_client_id:
                        if remaining_paths[4] in ["users"]:
                            if remaining_paths[6] in ["sms"]:
                                if remaining_paths[7] in ["nidVerification"]:
                                    return super().__call__(*remaining_paths[7:])
                        elif remaining_paths[4] in ["cardToIban"]:
                            return super().__call__(*remaining_paths[4:])

        raise HttpNotFound()
