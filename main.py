import asyncio
import os
from API.cloudpay_api import CloudPayClient

CLOUDPAY_LOGIN = os.getenv("PublicID", "login")
CLOUDPAY_PASSWORD = os.getenv("APISecret", "password")


async def main():
    a = await CloudPayClient.create(CLOUDPAY_LOGIN, CLOUDPAY_PASSWORD)
    resp = await a.pay_with_crypto(amount=50, ip_address="127.0.0.0", cryptogram='sfdsf')


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())