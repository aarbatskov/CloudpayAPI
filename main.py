import asyncio
import os

from aiohttp import TCPConnector
from base import AbstractInteractionClient

CLOUDPAY_LOGIN = os.getenv("PublicID")
CLOUDPAY_PASSWORD = os.getenv("APISecret")


class CloudPayClient(AbstractInteractionClient):

    def __init__(self):
        self.CONNECTOR = None
        self.base_url = "https://reqres.in/api/"
        super().__init__()

    @classmethod
    async def create(cls):
        self = cls()
        self.CONNECTOR = TCPConnector

    async def pay(self):
        url = self.endpoint_url('users?page=2', self.base_url)
        resp = await self.get(interaction_method='method', url=url)
        await self.close()
        return resp



async def main():
    a = CloudPayClient()
    await a.create()
    resp = await a.pay()
    print(resp)


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())