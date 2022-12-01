from decimal import Decimal

from aiohttp import TCPConnector, BasicAuth
from API.base import AbstractInteractionClient
from API.models import Secure3D, Transaction


class CloudPayClient(AbstractInteractionClient):

    def __init__(self, login: str, password: str):
        self.CONNECTOR = None
        self.SERVICE = 'cloudpay'
        self.login = login
        self.password = password
        self.base_url = "https://api.cloudpayments.ru/"
        super().__init__()

    @classmethod
    async def create(cls, login: str, password: str):
        self = cls(login, password)
        self.CONNECTOR = TCPConnector()
        return self

    def _get_authorisation_headers(self):
        return BasicAuth(self.login, self.password)

    async def pay_with_crypto(self, amount: Decimal,
                              ip_address: str,
                              cryptogram: str,
                              two_stage: bool = False
                              ):
        data = {
            "Amount": amount,
            "IpAddress": ip_address,
            "CardCryptogramPacket": cryptogram,
        }
        relative_url = "payments/cards/auth" if two_stage else "payments/cards/charge"
        url = self.endpoint_url(relative_url, self.base_url)
        resp = await self.get(interaction_method='method',
                              url=url,
                              auth=self._get_authorisation_headers(),
                              data=data)
        await self.close()
        if resp.get("Model"):
            if two_stage:
                return Transaction.create(resp["Model"])
            else:
                return Secure3D.create(resp["Model"])
        return resp

    async def cancel_payed(self, crtyptogram: str):
        pass 
