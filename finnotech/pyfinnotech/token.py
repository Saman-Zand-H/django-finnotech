import base64
from urllib.parse import unquote, urlencode

import ujson

from .const import ALL_SCOPE_CLIENT_CREDENTIALS, SCOPE_FACILITY_SHAHKAR_GET
from .responses import AuthorizationSmsVerify, AuthorizationTokenSmsSend


class Token:
    __token_type__ = "CODE"

    scopes = []

    def __init__(self):
        pass

    @property
    def is_valid(self):
        raise NotImplementedError()

    def revoke(self):
        raise NotImplementedError()

    def refresh(self, *args, **kwargs):
        raise NotImplementedError()

    def generate_authorization_header(self):
        raise NotImplementedError()

    @classmethod
    def build_basic_authentication_token(cls, username, password):
        return base64.encodebytes(f"{username}:{password}".encode()).decode().strip()


class ClientCredentialToken(Token):
    __token_type__ = "CODE"

    def __init__(self, **kwargs):
        super().__init__()
        self.token = kwargs.get("value", None)
        self.refresh_token = kwargs.get("refreshToken", None)
        self.creation_date = kwargs.get("creationDate", None)
        self.life_time = kwargs.get("lifeTime", None)
        self.scopes = kwargs.get("scopes", None)

    @property
    def is_valid(self):
        return True

    def revoke(self):
        raise NotImplementedError()

    def refresh(self, http_client):
        # TODO: We should ues refresh token, but it's not based on RFC, so it's almost unusable
        new_token = self.__class__.fetch(http_client)
        self.token = new_token.token
        self.refresh_token = new_token.refresh_token
        self.creation_date = new_token.creation_date
        self.life_time = new_token.life_time
        self.scopes = new_token.scopes

    @classmethod
    def load(cls, raw_token, refresh_token=None):
        payload = ujson.loads(
            base64.decodebytes((raw_token.split(".")[1] + "==").encode()).decode()
        )
        payload.setdefault("refreshToken", refresh_token)
        return cls(value=raw_token, **payload)

    def generate_authorization_header(self):
        return {"Authorization": f"Bearer {self.token}"}

    # noinspection PyProtectedMember
    @classmethod
    def fetch(cls, http_client):
        """
        https://devbeta.finnotech.ir/v2/boomrang-get-clientCredential-token.html
        :return:
        """
        url = "/dev/v2/oauth2/token"

        encoded_basic_authentication = (
            base64.encodebytes(
                f"{http_client.client_id}:{http_client.client_secret}".encode()
            )
            .decode()
            .strip()
        )
        return cls(
            **http_client._execute(
                uri=url,
                body={
                    "grant_type": "client_credentials",
                    "nid": http_client.client_national_id,
                    "scopes": ",".join(list(set(http_client.scopes))),
                },
                method="post",
                headers={"Authorization": f"Basic {encoded_basic_authentication}"},
            ).get("result")
        )


class SmsAuthorization(Token):
    __token_type__ = "SMS"

    def __init__(self, **kwargs):
        super().__init__()
        self.token = kwargs.get("value", None)
        self.refresh_token = kwargs.get("refreshToken", None)
        self.creation_date = kwargs.get("creationDate", None)
        self.life_time = kwargs.get("lifeTime", None)
        self.scopes = kwargs.get("scopes", [SCOPE_FACILITY_SHAHKAR_GET])
        self.deposits = kwargs.get("deposits", None)
        self.bank = kwargs.get("bank", None)
        self.type = kwargs.get("type", None)
        self.user_national_id = kwargs.get("userId", None)

    @property
    def is_valid(self):
        return True

    def revoke(self):
        raise NotImplementedError()

    # noinspection PyProtectedMember
    def refresh(self, http_client):
        url = "/dev/v2/oauth2/token"

        encoded_basic_authentication = (
            base64.encodebytes(
                f"{http_client.client_id}:{http_client.client_secret}".encode()
            )
            .decode()
            .strip()
        )
        new_token = self.__class__(
            **http_client._execute(
                uri=url,
                body={
                    "grant_type": "refresh_token",
                    "token_type": "CODE",
                    "auth_type": "SMS",
                    "refresh_token": self.refresh_token,
                },
                method="post",
                headers={"Authorization": f"Basic {encoded_basic_authentication}"},
            ).get("result")
        )

        self.token = new_token.token
        self.refresh_token = new_token.refresh_token
        self.creation_date = new_token.creation_date
        self.life_time = new_token.life_time
        self.scopes = new_token.scopes
        self.deposits = new_token.deposits
        self.bank = new_token.bank
        self.type = new_token.type
        self.user_national_id = new_token.user_national_id

    @classmethod
    def load(cls, raw_token, refresh_token=None):
        payload = ujson.loads(
            base64.decodebytes((raw_token.split(".")[1] + "==").encode()).decode()
        )
        payload.setdefault("refreshToken", refresh_token)
        return cls(value=raw_token, **payload)

    def generate_authorization_header(self):
        return {"Authorization": f"Bearer {self.token}"}

    # noinspection PyProtectedMember
    @classmethod
    def request_sms(
        cls, http_client, target_phone, scopes, redirect_url
    ) -> AuthorizationTokenSmsSend:
        url = "/dev/v2/oauth2/authorize"

        params = {
            "client_id": http_client.client_id,
            "response_type": "code",
            "redirect_uri": redirect_url,
            "scope": ",".join(scopes) if isinstance(scopes, list) else scopes,
            "mobile": target_phone,
            "state": http_client._generate_track_id(),
            "auth_type": "SMS",
        }

        encoded_basic_authentication = cls.build_basic_authentication_token(
            http_client.client_id, http_client.client_secret
        )
        return AuthorizationTokenSmsSend(
            http_client._execute(
                uri=f"{url}?{unquote(urlencode(params))}",
                method="get",
                headers={"Authorization": f"Basic {encoded_basic_authentication}"},
                no_track_id=True,
            ).get("result")
        )

    # noinspection PyProtectedMember
    @classmethod
    def verify_sms(
        cls, http_client, target_phone, target_national_id, track_id, otp
    ) -> AuthorizationSmsVerify:
        url = "/dev/v2/oauth2/verify/sms"

        encoded_basic_authentication = cls.build_basic_authentication_token(
            http_client.client_id, http_client.client_secret
        )
        return AuthorizationSmsVerify(
            http_client._execute(
                uri=url,
                body={
                    "mobile": target_phone,
                    "otp": otp,
                    "nid": target_national_id,
                    "trackId": track_id,
                },
                method="post",
                headers={"Authorization": f"Basic {encoded_basic_authentication}"},
                no_track_id=True,
            ).get("result")
        )

    # noinspection PyProtectedMember
    @classmethod
    def request_token(cls, http_client, code, redirect_url):
        url = "/dev/v2/oauth2/token"

        encoded_basic_authentication = cls.build_basic_authentication_token(
            http_client.client_id, http_client.client_secret
        )
        return cls(
            **http_client._execute(
                uri=url,
                body={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_url,
                    "auth_type": "SMS",
                },
                method="post",
                headers={"Authorization": f"Basic {encoded_basic_authentication}"},
                no_track_id=True,
            ).get("result")
        )
