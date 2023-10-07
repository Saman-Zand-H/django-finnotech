class BaseFinnotechResponse:
    def __init__(self, payload):
        self.payload = payload

    @property
    def track_id(self):
        return self.payload.get("trackId", None)


class CardToIbanResponse(BaseFinnotechResponse):
    @property
    def is_valid(self):
        return self.payload.get("depositStatus", None) in ["02", "2"]  # FIXME: WTF

    @property
    def iban(self):
        return self.payload.get("IBAN", None)

    @property
    def bank_name(self):
        return self.payload.get("bankName", None)

    @property
    def deposit(self):
        return self.payload.get("deposit", None)

    @property
    def card(self):
        return self.payload.get("card", None)

    @property
    def deposit_status(self):
        return self.payload.get("depositStatus", None)

    @property
    def deposit_description(self):
        return self.payload.get("depositDescription", None)

    @property
    def deposit_comment(self):
        return self.payload.get("depositComment", None)

    @property
    def deposit_owners(self):
        return self.payload.get("depositOwners", [])

    @property
    def alert_code(self):
        return self.payload.get("alertCode", None)


class CardInquiryResponse(BaseFinnotechResponse):
    @property
    def is_valid(self):
        return self.payload.get("result", None) == "0"

    @property
    def full_name(self):
        return self.payload.get("name", None)


class IbanInquiryResponse(BaseFinnotechResponse):
    @property
    def is_valid(self):
        return self.payload.get("depositStatus", None) in ["02", "2"]  # FIXME: WTF

    @property
    def owner_first_name(self):
        # FIXME: What should we do with cards with more than one owner?
        if len(self.payload.get("depositOwners")) != 1:
            return None
        return self.payload.get("depositOwners")[0].get("firstName", None)

    @property
    def owner_last_name(self):
        if len(self.payload.get("depositOwners")) != 1:
            return None
        return self.payload.get("depositOwners")[0].get("lastName", None)


class StandardReliabilitySms(BaseFinnotechResponse):
    @property
    def result(self):
        return self.payload.get("result", None)


class AuthorizationTokenSmsSend(BaseFinnotechResponse):
    @property
    def sms_sent(self):
        return self.payload.get("smsSent", None)


class AuthorizationSmsVerify(BaseFinnotechResponse):
    @property
    def code(self):
        return self.payload.get("code", None)


class NationalcodeMobileVerification(BaseFinnotechResponse):
    @property
    def is_valid(self):
        return self.payload.get("result", {}).get("isValid", False)

    @property
    def status(self):
        return self.payload.get("status")


class PostalcodeInquiry(BaseFinnotechResponse):
    @property
    def province(self):
        return self.payload.get("result", {}).get("Province")

    @property
    def township(self):
        return self.payload.get("result", {}).get("TownShip")

    @property
    def zone(self):
        return self.payload.get("result", {}).get("Zone")

    @property
    def village(self):
        return self.payload.get("result", {}).get("Village")

    @property
    def locality_type(self):
        return self.payload.get("result", {}).get("LocalityType")

    @property
    def locality_name(self):
        return self.payload.get("result", {}).get("LocalityName")

    @property
    def locality_code(self):
        return self.payload.get("result", {}).get("LocalityCode")

    @property
    def sub_locality(self):
        return self.payload.get("result", {}).get("SubLocality")

    @property
    def street(self):
        return self.payload.get("result", {}).get("street")

    @property
    def street2(self):
        return self.payload.get("result", {}).get("street2")

    @property
    def house_number(self):
        return self.payload.get("result", {}).get("HouseNumber")

    @property
    def floor(self):
        return self.payload.get("result", {}).get("Floor")

    @property
    def side_floor(self):
        return self.payload.get("result", {}).get("SideFloor")

    @property
    def building_name(self):
        return self.payload.get("result", {}).get("BuildingName")

    @property
    def description(self):
        return self.payload.get("result", {}).get("Description")

    # TODO: add is_valid


class BackChequesInqury(BaseFinnotechResponse):
    ...
