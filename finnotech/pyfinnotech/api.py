import logging
from json import JSONDecodeError
from logging import Logger
from uuid import uuid4

import requests

from .const import (
    SCOPE_BOOMRANG_SMS_SEND_EXECUTE,
    SCOPE_BOOMRANG_SMS_VERIFY_EXECUTE,
    SCOPE_BOOMRANG_TOKEN_DELETE,
    SCOPE_BOOMRANG_TOKENS_GET,
    SCOPE_BOOMRANG_WAGES_GET,
    SCOPE_CREDIT_SMS_BACK_CHEQUES_GET,
    SCOPE_CREDIT_SMS_FACILITY_INQUIRY_GET,
    SCOPE_ECITY_CC_POSTAL_CODE_INQUIRY,
    SCOPE_FACILITY_SHAHKAR_GET,
    URL_MAINNET,
    URL_SANDBOX,
)
from .exceptions import FinnotechException, FinnotechHttpException
from .responses import (
    BackChequesInqury,
    NationalcodeMobileVerification,
    PostalcodeInquiry,
)
from .token import ClientCredentialToken, Token


class FinnotechApiClient:
    def __init__(
        self,
        client_id,
        client_secret=None,
        client_national_id=None,
        scopes=None,
        is_sandbox=False,
        logger: Logger = None,
        requests_extra_kwargs: dict = None,
        client_credential_token=None,
        client_credential_refresh_token=None,
        authorization_token=None,
        base_url=None,
    ):
        self.server_url = base_url or (
            URL_SANDBOX if is_sandbox is True else URL_MAINNET
        )
        self.logger = logger or logging.getLogger("pyfinnotech")
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_national_id = client_national_id
        self.scopes = scopes or [
            SCOPE_BOOMRANG_SMS_SEND_EXECUTE,
            SCOPE_BOOMRANG_SMS_VERIFY_EXECUTE,
            SCOPE_BOOMRANG_TOKEN_DELETE,
            SCOPE_BOOMRANG_TOKENS_GET,
            SCOPE_CREDIT_SMS_BACK_CHEQUES_GET,
            SCOPE_CREDIT_SMS_FACILITY_INQUIRY_GET,
            SCOPE_ECITY_CC_POSTAL_CODE_INQUIRY,
            SCOPE_FACILITY_SHAHKAR_GET,
            SCOPE_BOOMRANG_WAGES_GET,
        ]
        self.requests_extra_kwargs = requests_extra_kwargs or {}
        self._client_credential_token = None
        if client_credential_token is not None:
            self._client_credential_token = ClientCredentialToken.load(
                raw_token=client_credential_token,
                refresh_token=client_credential_refresh_token,
            )

    @classmethod
    def _generate_track_id(cls):
        return uuid4().__str__()

    @property
    def client_credential(self):
        if (
            self._client_credential_token is not None
            and self._client_credential_token.is_valid is True
        ):
            pass
        else:
            self._client_credential_token = ClientCredentialToken.fetch(self)
        return self._client_credential_token

    def _execute(
        self,
        uri,
        method="get",
        params=None,
        headers=None,
        body=None,
        token: Token = None,
        error_mapper=None,
        no_track_id=False,
    ):
        params = params or dict()
        headers = headers or dict()
        track_id = self._generate_track_id() if no_track_id is False else None
        if track_id is not None:
            params.setdefault("trackId", track_id)
        self.logger.debug(
            f"Requesting"
            f" on {uri} with id:{track_id}"
            f" with parameters: {'.'.join(str(params))}"
        )

        if token is not None:
            headers = {**headers, **token.generate_authorization_header()}

        try:
            response = requests.request(
                method,
                "".join([self.server_url, uri]),
                params=params,
                headers=headers,
                json=body,
                **self.requests_extra_kwargs,
            )

            if response.status_code == 403:
                self.logger.info("Trying to refresh token")
                token.refresh(self)

                response = requests.request(
                    method,
                    "".join([self.server_url, uri]),
                    params=params,
                    headers=headers,
                    json=body,
                    **self.requests_extra_kwargs,
                )

            if response.status_code != 200:
                raise FinnotechHttpException(response, self.logger)

            try:
                return response.json()
            except JSONDecodeError as e:
                raise FinnotechHttpException(
                    response=response, logger=self.logger, underlying_exception=e
                )

        except FinnotechHttpException as e:
            raise e

        except Exception as e:
            raise FinnotechException(f"Request error: {str(e)}", logger=self.logger)

    def national_code_mobile_verification(self, national_id, mobile):
        url = f"/facility/v2/clients/{self.client_id}/shahkar/verify?nationalCode={national_id}&mobile={mobile}"

        return NationalcodeMobileVerification(
            self._execute(
                uri=url,
                token=self.client_credential,
            )
        )

    def postal_code_inquiry(self, postal_code):
        url = f"/ecity/v2/clients/{self.client_id}/postalCode?postalCode={postal_code}"

        return PostalcodeInquiry(
            self._execute(
                uri=url,
                token=self.client_credential,
            )
        )

    def back_cheques_inquiry(self, national_id: str, token: str):
        url = f"/credit/v2/clients/HammerszLeasing/users/{national_id}/sms/backCheques"

        return BackChequesInqury(self._execute(uri=url, token=token))
