import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Any

from pydantic import PrivateAttr

from sirius import common
from sirius.common import DataClass, Currency
from sirius.constants import EnvironmentSecret
from sirius.http_requests import AsyncHTTPSession, HTTPResponse
from sirius.wise import constants


def get_http_session(api_key: str) -> AsyncHTTPSession:
    api_key = common.get_environmental_secret(EnvironmentSecret.WISE_API_KEY) if api_key is None else api_key
    return AsyncHTTPSession(constants.URL, {"Authorization": f"Bearer {api_key}"})


class AccountType(Enum):
    STANDARD = "STANDARD"
    SAVINGS = "SAVINGS"


class ProfileType(Enum):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"


class Transaction(DataClass):
    amount: Decimal
    currency: Currency
    description: str
    running_balance: Decimal


class Account(DataClass):
    id: int
    profile_id: int
    currency: Currency
    type: AccountType
    name: str
    balance: Decimal
    _http_session: AsyncHTTPSession = PrivateAttr()

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._http_session = data["http_session"]

    async def get_transactions(self, from_time: datetime.datetime | None = None, to_time: datetime.datetime | None = None, number_of_past_hours: int | None = None) -> List[Transaction]:
        transaction_list: List[Transaction] = []
        number_of_past_hours = number_of_past_hours if number_of_past_hours else 24
        from_time = from_time if from_time else datetime.datetime.now() - datetime.timedelta(hours=number_of_past_hours)
        to_time = to_time if to_time else datetime.datetime.now()
        url: str = constants.ENDPOINT__BALANCE__GET_TRANSACTIONS.replace("$profileId", str(self.profile_id)).replace("$balanceId", str(self.id))
        query_params: Dict[str, Any] = {
            "currency": self.currency.value,
            "intervalStart": f"{from_time.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().split('+')[0]}Z",
            "intervalEnd": f"{to_time.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().split('+')[0]}Z",
            "type": "COMPACT"
        }

        response: HTTPResponse = await self._http_session.get(url, query_params)
        for data in response.data["transactions"]:
            transaction = Transaction(
                amount=Decimal(str(data["amount"]["value"])),
                currency=Currency(data["amount"]["currency"]),
                description=data["details"]["description"],
                running_balance=Decimal(str(data["runningBalance"]["value"]))
            )
            transaction_list.append(transaction)

        return transaction_list


class Profile(DataClass):
    id: int
    type: ProfileType
    _account_list: List[Account] = []
    _http_session: AsyncHTTPSession = PrivateAttr()

    @property
    async def account_list(self) -> List[Account] | None:
        if len(self._account_list) != 0:
            return self._account_list

        url: str = constants.ENDPOINT__ACCOUNT__GET_ALL.replace("$profileId", str(self.id))
        response: HTTPResponse = await self._http_session.get(url)
        for data in response.data:
            account = Account(
                id=data["id"],
                profile_id=self.id,
                currency=Currency(data["totalWorth"]["currency"]),
                type=AccountType(data["type"]),
                name=data["name"] if data["name"] else f"{data['totalWorth']['currency']} Bank Account",
                balance=Decimal(data["totalWorth"]["value"]),
                http_session=self._http_session
            )
            self._account_list.append(account)

        return self._account_list

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self._http_session = data["http_session"]


class WiseAccount(DataClass):
    personal_profile: Profile
    _http_session: AsyncHTTPSession
    business_profile: Profile | None = None

    @staticmethod
    async def get(api_key: str | None = None) -> "WiseAccount":
        http_session: AsyncHTTPSession = get_http_session(api_key)
        response: HTTPResponse = await http_session.get(constants.ENDPOINT__PROFILE__GET_ALL)
        profile_list: List[Profile] = [Profile(id=data["id"], type=ProfileType(data["type"]), http_session=http_session) for data in response.data]
        personal_profile: Profile = next(filter(lambda p: p.type == ProfileType.PERSONAL, profile_list))
        business_profile: Profile = next(filter(lambda p: p.type == ProfileType.BUSINESS, profile_list), None)

        return WiseAccount(personal_profile=personal_profile, business_profile=business_profile, _http_session=http_session)
