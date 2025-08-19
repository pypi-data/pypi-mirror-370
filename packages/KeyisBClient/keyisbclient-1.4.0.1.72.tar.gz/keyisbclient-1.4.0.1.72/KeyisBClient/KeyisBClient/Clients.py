
import os
import httpx
import asyncio
import typing as _typing
import logging as logging2
logging2.basicConfig(level=logging2.INFO)
from concurrent.futures import ThreadPoolExecutor

from KeyisBLogging import logging

from .Exceptions import Exceptions
from .core import DNS, ProtocolsManager
from .models import Url, Request, Response








class AsyncClient:
    def __init__(self):
        pass

    async def get(self,
                url: _typing.Union[Url, str],
                data=None,
                json: _typing.Optional[dict] = None,
                cookies: dict = None,
                headers=None) -> Response:
        return await self.request("GET", url=url, data=data, json=json, cookies=cookies, headers=headers)

    async def request(self,
                      method: str,
                      url: _typing.Union[Url, str],
                      data: _typing.Mapping[str, _typing.Any] | None = None,
                      json: dict | None = None,
                      cookies: dict = None,
                      protocolVersion: _typing.Optional[str] = None,
                        content: _typing.Any = None,
                      **kwargs,
                      ) -> Response:
        """
        Build and send a async request.
        
        ```python
        webAsyncClient = KeyisBClient.AsyncClient()
        async def func():
            response = await webAsyncClient.request('GET', 'https://example.com/example')
            body = response.json()
        ```
        """
        
        if isinstance(url, str):
            url = Url(url)
        logging.info(f'Url -> {url}')

        request = Request(
            method,
            url,
            data=data,
            json=json,
            cookies=cookies,
            content=content
            )
        

        return await ProtocolsManager.requestAsync(request)

        


    async def stream(self,
                     method: str,
                     url: _typing.Union[Url, str],
                     **kwargs
                     ) -> _typing.AsyncIterator[Response]:
        
        if isinstance(url, str):
            url = Url(url)

        logging.info(f'Url -> {url}')

        request = Request(
            method,
            url,
            **kwargs
            )
        
        async for response in ProtocolsManager.streamAsync(request):
            yield response





class Client:
    def __init__(self):
        pass

    def get(self,
            url: _typing.Union[Url, str],
            json: _typing.Optional[dict] = None,
            data=None,
            cookies: _typing.Optional[dict] = None,
            headers=None
            ) -> Response:
        """
        Build and send a get request.

        ```python
        webClient = KeyisBClient.Client()
        response = webClient.request('GET', 'https://example.com/example')
        body = response.json()
        ```
        
        """
        return self.request("GET", url=url, data=data, json=json, cookies=cookies, headers=headers)

    def request(self,
                method: str,
                url: _typing.Union[Url, str],
                json: _typing.Optional[dict] = None,
                data: _typing.Mapping[str, _typing.Any] | None = None,
                cookies: _typing.Optional[dict] = None,
                protocolVersion: _typing.Optional[str] = None,
                content: _typing.Any = None,
                **kwargs,
                ) -> Response:
        """
        Build and send a request.
        
        ```python
        webClient = KeyisBClient.Client()
        response = webClient.request('GET', 'https://example.com/example')
        body = response.json()
        ```
        """
        
        if isinstance(url, str):
            url = Url(url)
        logging.info(f'Url -> {url}')

        request = Request(
            method,
            url,
            data=data,
            json=json,
            cookies=cookies,
            content=content
            )
        

        return ProtocolsManager.requestSync(request)