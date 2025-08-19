
import re
import os
import typing as _typing
from typing import Optional, List, Literal, Any, Dict, Union, Mapping
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import asyncio
import httpx
from KeyisBLogging import logging

from .models import Url, DNSObject, Request, Response, ClientObject


class __DNS:
    async def getHostAsync(self, domain: str) -> Optional[str]:
        """
        Получение DNS-адреса из сети DNS GW

        :param domain: 
        """
        dnsObject = DNSObject(domain)
        await dnsObject.requestAsync()
        return dnsObject.host()
DNS = __DNS()



class __ProtocolsManager:
    def __init__(self):
        self.cores: Dict[str, Dict[str, Union[str, ClientObject]]] = {}
    async def requestAsync(self, request: Request) -> Response:
        scheme = request.url.scheme

        if scheme not in self.cores:
            logging.error(f'Unknown scheme: {scheme} in request {request.url}!')
            return Response(-1) # Unknown scheme

        if scheme.startswith('gw') or scheme.startswith('mmb'): # Если протокол mmb, то это сразу внутреняя dns система
            
            dnsObject = DNSObject(request.url.hostname)
            await dnsObject.requestAsync() # получаем DNS-запись о сервере

            protocolInfo = dnsObject.protocolInfo()

            protocolVersion = protocolInfo.get('version', '$last')
            request.dnsObject = dnsObject
        else:
            protocolVersion = '$default'

            
        if protocolVersion.startswith('$'):
            protocolVersion: str = self.cores[scheme][protocolVersion] # type: ignore
        
        
        client: ClientObject  = self.cores[scheme][protocolVersion] # type: ignore
        return await client.requestAsync(request)
    def requestSync(self, request: Request) -> Response:
        scheme = request.url.scheme

        if scheme not in self.cores:
            logging.error(f'Unknown scheme: {scheme} in request {request.url}!')
            return Response(-1) # Unknown scheme

        if scheme.startswith('gw') or scheme.startswith('mmb'): # Если протокол mmb, то это сразу внутреняя dns система
            
            dnsObject = DNSObject(request.url.hostname)
            dnsObject.request() # получаем DNS-запись о сервере

            protocolInfo = dnsObject.protocolInfo()

            protocolVersion = protocolInfo.get('version', '$last')
            request.dnsObject = dnsObject
        else:
            protocolVersion = '$default'

            
        if protocolVersion.startswith('$'):
            protocolVersion: str = self.cores[scheme][protocolVersion] # type: ignore
        
        
        client: ClientObject  = self.cores[scheme][protocolVersion] # type: ignore
        return client.requestSync(request)
    
    def addClient(self, client: ClientObject):
        for scheme, versions in client.protocols.items():
            self.cores[scheme] = {}

            for version in versions['versions']:
                self.cores[scheme][version] = client
            
            if 'last' in versions:
                self.cores[scheme]['$last'] = versions['last']
            else:
                self.cores[scheme]['$last'] = versions['versions'][-1]

            if 'default' in versions:
                self.cores[scheme]['$default'] = versions['default']
            else:
                self.cores[scheme]['$default'] = versions['versions'][-1]

    async def streamAsync(self, request: Request) -> _typing.AsyncIterator[Response]:
        scheme = request.url.scheme

        if scheme not in self.cores:
            logging.error(f'Unknown scheme: {scheme} in request {request.url}!')
            yield Response(-1) # Unknown scheme

        if scheme.startswith('gw') or scheme.startswith('mmb'): # Если протокол mmb, то это сразу внутреняя dns система
            
            dnsObject = DNSObject(request.url.hostname)
            await dnsObject.requestAsync() # получаем DNS-запись о сервере

            protocolInfo = dnsObject.protocolInfo()

            protocolVersion = protocolInfo.get('version', '$last')
            request.dnsObject = dnsObject
        else:
            protocolVersion = '$default'

            
        if protocolVersion.startswith('$'):
            protocolVersion: str = self.cores[scheme][protocolVersion] # type: ignore
        
        
        client: ClientObject  = self.cores[scheme][protocolVersion] # type: ignore

        

        async for response in await client.streamAsync(request):
            yield response

ProtocolsManager = __ProtocolsManager()


