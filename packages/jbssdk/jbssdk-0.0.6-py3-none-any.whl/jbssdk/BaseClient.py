import abc
import os
from typing import Optional

import dotenv
import httpx

from . import timeout, limits

dotenv.load_dotenv()


class JBSBaseClient(abc.ABC):
    def __init__(self, USERNAME: Optional[str] = None, PASSWORD: Optional[str] = None,
                 TENANTCODE: Optional[str] = None, BASEURL: Optional[str] = None, JBS_TOKEN: Optional[str] = None, ):
        if USERNAME is None:
            self.USERNAME = os.getenv('JBS_USER_NAME')
        else:
            self.USERNAME = USERNAME
        if PASSWORD is None:
            self.PASSWORD = os.getenv('JBS_PASSWD')
        else:
            self.PASSWORD = PASSWORD
        if TENANTCODE is None:
            self.TENANTCODE = os.getenv('JBS_TENANTCODE')
        else:
            self.TENANTCODE = TENANTCODE
        if BASEURL is None:
            self.BASEURL = os.getenv('JBS_BACKEND_URL') or "https://jbs.backend.smyun.net"
        else:
            self.BASEURL = BASEURL
        if JBS_TOKEN is None:
            self.JBS_TOKEN = os.getenv('JBS_TOKEN')
        else:
            self.JBS_TOKEN = None
        self.COMPLETION_URL = f'''{self.BASEURL}/link/dataLink/completions'''

    async def getGoodHeader(self):
        header = {'Authorization': f'Bearer {await self.loginToJBS()}'}
        return header

    def getTokenHeader(self):
        header = {'Authorization': f'Bearer {self.JBS_TOKEN}'}
        return header

    def build_query_params(self, **kwargs) -> dict:

        return {key: value for key, value in kwargs.items() if value is not None}

    async def loginToJBS(self):
        payload = {
            "username": self.USERNAME,
            "password": self.PASSWORD,
            "tenantCode": self.TENANTCODE
        }
        async with httpx.AsyncClient(verify=False, timeout=timeout, limits=limits) as client:
            result = await client.post(f'{self.BASEURL}/login', json=payload)
            try:
                if result.status_code == 200:
                    return result.json()['datas']['token']
            except Exception as e:
                print(e)
                return None
