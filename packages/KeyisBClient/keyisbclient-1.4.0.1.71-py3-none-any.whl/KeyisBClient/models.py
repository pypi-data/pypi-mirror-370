
import re
import os
from typing import Optional, List, Literal, Any, Dict, Union, Mapping, Callable, AsyncIterator, overload
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import asyncio
import httpx
from KeyisBLogging import logging

from .Exceptions import Exceptions
from .dnsCore import DNSCore
import msgpack


class DNSObject:
    def __init__(self, domain: str):
        self.domain: str = domain
        self.ip: str = None # type: ignore
        self.port: int = None # type: ignore
        self.protocol: str = None # type: ignore
        self.protocol_version: str = '$last'
        self.__rules: str = None # type: ignore
        self.__connection_protocol: str = 'https'
        self.__connection_protocol_version: str = '$last'
    def host(self) -> Optional[str]:
        if None in (self.ip, self.port):
            return None
        return f'{self.ip}:{self.port}'
    def url(self) -> str:
        return f"{self.protocol}://{self.host()}"
    def __str__(self) -> str:
        return str(self.host())
    async def requestAsync(self) -> Optional[str]:
        for dnsHostElement in DNSCore.hosts:
            query_url = f"{dnsHostElement['host']}/servers?d={self.domain}"
    
            try:
                response = await DNSCore._connectionAsync.get(query_url)
                if response.status_code == 404:
                        logging.error(f"DNS request failed: {response.status_code} - Server Not Found")
                        raise Exceptions.DNS.DNSServerNotFoundError("DNS server not found")
                elif response.status_code == 403:
                        logging.error(f"DNS request failed: {response.status_code} - Access Denied")
                        raise Exceptions.DNS.DNSAccessDeniedError("Access denied to DNS server")
                elif response.status_code == 500:
                        logging.error(f"DNS request failed: {response.status_code} - Server Failure")
                        raise Exceptions.DNS.DNSServerFailureError("DNS server failure")
                elif response.status_code != 200:
                        logging.error(f"DNS request failed: {response.status_code}")
                        raise Exceptions.DNS.UnexpectedError("Invalid DNS response status")

                result = response.json()

                self.ip = result.get('ip')
                if not self.ip:
                    raise Exceptions.DNS.DNSResponseError("Invalid DNS response format: 'ip' field is missing")

                self.port = result.get('port', 443)
                self.protocol = result.get('protocol', 'https')
                self.__rules = result.get('rules')

                self.protocol_version = result.get('protocol_version', '$last')
                self.__connection_protocol = result.get('connection_protocol')
                self.__connection_protocol_version = result.get('connection_protocol_version')

                return self.host()

            except httpx.TimeoutException:
                logging.debug("Connection timeout during DNS resolution")
                #raise Exceptions.DNS.DNSTimeoutError("Timeout during DNS resolution")
            except httpx.RequestError as e:
                logging.debug(f"Request error during DNS resolution: {e}")
                #raise Exceptions.DNS.ErrorConnection("Connection error during DNS resolution")
            except Exception as e:
                logging.debug(f"Unexpected error during DNS resolution: {e}")
                #raise Exceptions.DNS.UnexpectedError("Unexpected error during DNS resolution")
    def request(self) -> Optional[str]:
        for dnsHostElement in DNSCore.hosts:
            query_url = f"{dnsHostElement['host']}/servers?d={self.domain}"
    
            try:
                response = DNSCore._connectionSync.get(query_url)
                if response.status_code == 404:
                        logging.error(f"DNS request failed: {response.status_code} - Server Not Found")
                        raise Exceptions.DNS.DNSServerNotFoundError("DNS server not found")
                elif response.status_code == 403:
                        logging.error(f"DNS request failed: {response.status_code} - Access Denied")
                        raise Exceptions.DNS.DNSAccessDeniedError("Access denied to DNS server")
                elif response.status_code == 500:
                        logging.error(f"DNS request failed: {response.status_code} - Server Failure")
                        raise Exceptions.DNS.DNSServerFailureError("DNS server failure")
                elif response.status_code != 200:
                        logging.error(f"DNS request failed: {response.status_code}")
                        raise Exceptions.DNS.UnexpectedError("Invalid DNS response status")

                result = response.json()

                self.ip = result.get('ip')
                if not self.ip:
                    raise Exceptions.DNS.DNSResponseError("Invalid DNS response format: 'ip' field is missing")

                self.port = result.get('port', 443)
                self.protocol = result.get('protocol', 'https')
                self.__rules = result.get('rules')

                self.protocol_version = result.get('protocol_version', '$last')
                self.__connection_protocol = result.get('connection_protocol')
                self.__connection_protocol_version = result.get('connection_protocol_version')

                return self.host()

            except httpx.TimeoutException:
                logging.debug("Connection timeout during DNS resolution")
                #raise Exceptions.DNS.DNSTimeoutError("Timeout during DNS resolution")
            except httpx.RequestError as e:
                logging.debug(f"Request error during DNS resolution: {e}")
                #raise Exceptions.DNS.ErrorConnection("Connection error during DNS resolution")
            except Exception as e:
                logging.debug(f"Unexpected error during DNS resolution: {e}")
                #raise Exceptions.DNS.UnexpectedError("Unexpected error during DNS resolution")

    def protocolVersion(self) -> str:
        return self.protocol_version or '$last'
    def protocolInfo(self) -> Dict[str, Any]:
        return {
            'protocol': self.protocol,
            'protocol_version': self.protocol_version,
            'connection_protocol': self.__connection_protocol,
            'connection_protocol_version': self.__connection_protocol_version,
            'rules': self.__rules
        }




class Url:

    @overload
    def __init__(self): ...
    
    @overload
    def __init__(self, url: str): ...

    @overload
    def __init__(self, url: 'Url'): ...

    @overload
    def __init__(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'OPTION'], url: str): ...

    @overload
    def __init__(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'OPTION'], url: 'Url'): ...
         
    def __init__(self, method_or_url: Optional[Union[Literal['GET', 'POST', 'PUT', 'DELETE', 'OPTION'], 'Url', str]] = None, url: Optional[Union[str, 'Url']] = None):
        
        if method_or_url is not None:
            if url is None:
                # тогда url задан как method_or_url
                url = method_or_url
                self.method = None
            else:
                # тогда url задан отдельно
                self.method = method_or_url
        else:
            url = None
            self.method = None
        
        self.interpreter: Optional[str] = None
        self.scheme: str = None # type: ignore
        self.hostname: str = None # type: ignore
        self.path: str = None # type: ignore
        self.query: str = None # type: ignore
        self.fragment: str = None # type: ignore
        self.params: dict = None # type: ignore
        self.protocolVersion: str = '$last'

        if url:
            self.setUrl(url)
        
        

    def __parse_url(self, url_str: str):
        pattern = r"^(?P<interpreter>[A-Za-z0-9_]+):(?P<rest>[A-Za-z0-9_]+://.+)$"
        match = re.match(pattern, url_str)
        
        if match:
            interpreter = match.group("interpreter")
            rest_url = match.group("rest")
        else:
            interpreter = None
            rest_url = url_str
    
        parsed_url = urllib.parse.urlparse(rest_url)


        self.interpreter = interpreter
        self.scheme = parsed_url.scheme if parsed_url.scheme != '' else None # type: ignore

        self.hostname = parsed_url.netloc if parsed_url.netloc != '' else None # type: ignore
        self.path = parsed_url.path
        self.query = parsed_url.query
        self.fragment = parsed_url.fragment
        self.params = self.__parse_params(parsed_url.query)

    def __parse_params(self, query_str: str) -> dict:

        parsed = urllib.parse.parse_qs(query_str)
        cleaned = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        return cleaned

    def __str__(self):
        return self.getUrl()
    
    def setUrl(self, url: Union['Url', str]):

        if not isinstance(url, str):
             url = str(url)

        if url == '':
            url = '/'
        
        self.__parse_url(url)
        

    def getUrl(self, parts: List[Literal['interpreter', 'scheme', 'hostname', 'path', 'params', 'fragment']] = ['scheme', 'hostname', 'path', 'params', 'fragment']) -> str:
        try:
            scheme = self.scheme if'scheme' in parts else ''
            hostname = self.hostname if 'hostname' in parts else ''
            path = self.path if 'path' in parts else ''

            if self.params is None:
                self.params = {}
            params = urllib.parse.urlencode(self.params, doseq=True) if 'params' in parts else ''
            
            fragment = self.fragment if 'fragment' in parts else ''

            if scheme is None: scheme = ''
            if hostname is None: hostname = ''



            url = urllib.parse.urlunparse((
                scheme, hostname, path, '', params, fragment
            ))

            url = f'{self.interpreter}:{url}' if 'interpreter' in parts and self.interpreter is not None else url


            if 'path' not in parts:
                if url.endswith(':'):
                    url = url[:-1]

            if 'scheme' not in parts:
                if url.startswith('//'):
                    url = url[2:]

            
            return url

        except Exception as e:
            logging.error(f"Failed to get URL: {e} from scheme: {self.scheme}, hostname: {self.hostname}, path: {self.path}, params: {self.params}, fragment: {self.fragment}")

            raise e
        


    def isSchemeSecure(self) -> bool:
        return self.scheme in ('https', 'mmbps')
    
    def getDafaultUrl(self) -> 'Url':
        _url = Url(self.getUrl())

        if _url.scheme in ('mmbp', 'mmbps'):

            dnsObject = DNSObject(_url.hostname)
            host = dnsObject.request()

            if not host:
                raise Exceptions.DNS.UnexpectedError()
            
            _url.hostname = host
                 
        if _url.scheme == 'mmbps': _url.scheme = 'https'

        return _url


    def serialise(self):
        return self.getUrl(['interpreter', 'scheme', 'hostname', 'path', 'params', 'fragment'])

    def deserialise(self, serializeUrl: str):
        self.setUrl(serializeUrl)
        
            

    def __run_asyncio_task_fetch_sync__(self, hostname):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            import KeyisBClient
            result = loop.run_until_complete(KeyisBClient.Client.getDNS(hostname))
        finally:
            loop.close()
        return result








class Request:
    def __init__(
        self,
        method: str,
        url: Url,
        content = None,
        data = None,
        files = None,
        json = None,
        params = None,
        headers = None,
        cookies = None,
        auth = None,
        follow_redirects: bool = True,
        timeout = None,
        extensions = None
    ) -> None:
        self.method = method
        self.url = url
        self.data = data
        self.json = json
        self.params = params
        self.headers = headers
        self.cookies = cookies
        self.auth = auth
        self.follow_redirects = follow_redirects
        self.timeout = timeout
        self.extensions = extensions
        self.content = content
        self.files = files

        self.dnsObject: Optional['DNSObject'] = None




HeaderTypes = Union[
    Mapping[str, str],
    Mapping[bytes, bytes]
]

class Response:
    """
    Represents a response from a server

    Attributes:
    
        status_code (int): The status code of the response. > 0 like HTTP status codes.
        
        json() (Any): The JSON data from the response if it's a JSON response.


    """
    def __init__(
        self,
        status_code: int,
        headers = HeaderTypes,
        content = Optional[bytes],
        text: Any = None,
        json = None,
        stream = None,
        request = None,
        url: Url = None,
        extensions = None,
        history: list['Response'] | None = None,
        default_encoding: str | Callable[[bytes], str] = "utf-8",
    ) -> None:
        self.status_code = status_code
        "The status code of the response. > 0 like HTTP "
        self.text = text
        "The response body as a string."

        self._request: Request | None = request
        self.__json = json
        self.url: Url = url

        self._content = content
        self._headers = headers
    def json(self) -> Any:
        return self.__json
    
    @property
    def content(self) -> bytes:
         return self._content


    @property
    def headers(self) -> HeaderTypes:
         return self._headers




class ClientObject:
    def __call__(self, *args: Any, **kwds: Any) -> Any: ...
    protocols: dict
    async def requestAsync(self, request: Request) -> Response: ...
    def requestSync(self, request: Request) -> Response: ...
    async def streamAsync(self, request: Request) -> AsyncIterator[Response]: ...









