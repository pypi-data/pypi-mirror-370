from __future__ import annotations
import msgpack
from typing import Optional
import re
import os
from functools import lru_cache
from typing import Iterable, List, NamedTuple, Optional, Tuple, Union, Dict, Any, Literal, overload, cast
from ..models import Url
import asyncio
import anyio

from ._func import guess_type, extract_template_vars, render_pct_async


def _pack(mode: int, flag: bool, number: int) -> bytes:
    if not (1 <= mode <= 4): raise ValueError("mode должен быть 1..4")
    if number >= (1 << 61): raise ValueError("number должен быть < 2^61")
    value = ((mode - 1) & 0b11) << 62
    value |= (1 << 61) if flag else 0
    value |= number & ((1 << 61) - 1)
    return value.to_bytes(8, "big")

def _unpack(data: bytes):
    if len(data) < 8: raise Exception('len < 8')
    value = int.from_bytes(data[:8], "big")
    mode = ((value >> 62) & 0b11) + 1
    flag = bool((value >> 61) & 1)
    number = value & ((1 << 61) - 1)
    return mode, flag, number


class CORSObject:
    def __init__(self, allow_origins: List[str], allow_credentials: bool = True, allow_methods: List[str] = ["*"], allow_headers: List[str] = ["*"]) -> None:
        self._allow_origins = allow_origins
        self._allow_credentials = allow_credentials
        self._allow_methods = allow_methods
        self._allow_headers = allow_headers

    def addAllowOrigins(self, allow_origins: List[str]) -> None:
        self._allow_origins += allow_origins
    
    def serialize(self) -> Dict[str, Union[str, bool, List[str]]]:
        return {
            'allow_origins': self._allow_origins,
            'allow_credentials': self._allow_credentials,
            'allow_methods': self._allow_methods,
            'allow_headers': self._allow_headers
        }

    @staticmethod
    def deserialize(data: Dict[str, Union[str, bool, List[str]]]) -> 'CORSObject':
        return CORSObject(
            allow_origins=data.get('allow_origins', []),
            allow_credentials=data.get('allow_credentials', False),
            allow_methods=data.get('allow_methods', ['*']),
            allow_headers=data.get('allow_headers', ['*'])
        )

class TemplateObject:
    def __init__(self,
                 vars_backend: Optional[Dict[str, Any]] = None,
                 vars_proxy: Optional[List[str]] = None,
                 vars_frontend: Optional[List[str]] = None
                 ) -> None:
        """
        
        - local side - "%{var}"

        - proxy - "!{var}"

        - user side - "&{var}"

        To substitute variables on the proxy and client, they must be requested from the server. To do this, add them to vars_proxy and vars_frontend

        If a template starts with "%" it is substituted on the server (gn:backend).

        If a template starts with "!" it is substituted on the proxy (gn:proxy).

        If a template starts with "&" it is substituted on the user side (gn:frontend).
        """

        self._vars_backend = vars_backend or {}
        self._vars_proxy = vars_proxy
        self._vars_frontend = vars_frontend
    
    def addVariable(self, name: str, value: Optional[Union[str, int, float, bool]], replacementPlace: Literal['backend', 'proxy', 'frontend'] = 'backend'):
        if not name.startswith(('%', "!", "&")):
            name = {'backend':"%", 'proxy':"!", 'frontend': "&"}[replacementPlace] + name

        if name.startswith('%'):
            self._vars_backend[name[1:]] = value
        elif name.startswith('!'):
            self._vars_proxy.append(name[1:])
        elif name.startswith('&'):
            self._vars_frontend.append(name[1:])
    
    
    def serialize(self) -> Dict[str, Union[Dict[str, Union[str, int, float, bool]], List[str]]]:
        d = {}
        
        if self._vars_proxy:
            d['proxy'] = self._vars_proxy

        if self._vars_frontend:
            d['frontend'] = self._vars_frontend
        
        return d

    @staticmethod
    def deserialize(data: Dict[str, Union[Dict[str, Union[str, int, float, bool]], List[str]]]) -> 'TemplateObject':
        return TemplateObject(
            None,
            data.get('proxy', {}),
            data.get('frontend', {})
        )

class FileObject:

    @overload
    def __init__(
        self,
        path: str,
        template: Optional[TemplateObject] = ...,
        name: Optional[str] = ...
    ) -> None: ...
    
    @overload
    def __init__(
        self,
        data: bytes,
        mime_type: str,
        template: Optional[TemplateObject] = ...,
        name: Optional[str] = ...
    ) -> None: ...

    def __init__(
        self,
        path_or_data: Union[str, bytes],
        mime_type: Optional[str] = None,
        template: Optional[TemplateObject] = None,
        name: Optional[str] = None
    ) -> None:
        self._path: Optional[str] = None
        self._data: Optional[bytes] = None
        self._mime_type: Optional[str] = None
        self._template: Optional[TemplateObject] = None
        self._name: Optional[str] = name

        self._is_assembly: Optional[Tuple[Optional[str], dict]] = None

        if isinstance(path_or_data, str):
            if template is None and mime_type is not None and not isinstance(mime_type, str):
                template = cast(TemplateObject, mime_type)
                mime_type = None

            if mime_type is not None:
                raise TypeError(
                    "При инициализации через path второй аргумент — это template, "
                    "mime_type указывать нельзя."
                )

            self._path = path_or_data
            self._mime_type = guess_type(path_or_data)
            self._template = template

        elif isinstance(path_or_data, bytes):
            self._data = path_or_data
            self._mime_type = mime_type
            self._template = template

        else:
            raise TypeError(f"path_or_data: ожидается str или bytes, получено {type(path_or_data)!r}")

    
    async def assembly(self) -> Tuple[Optional[str], dict]:
        """
        Assembles a file. Reads the file and substitutes templates.
        """
        if self._is_assembly is not None:
            return self._is_assembly

        if self._data is None:
            if not isinstance(self._path, str):
                raise Exception('Ошибка сбоки файла -> Путь к файлу не str')
            
            if not os.path.exists(self._path):
                raise Exception(f'Ошибка сбоки файла -> Файл не найден {self._path}')

            try:
                async with await anyio.open_file(self._path, mode="rb") as file:
                    self._data = await file.read()
            except Exception as e:
                raise Exception(f'Ошибка сбоки файла -> Ошиибка при чтении файла: {e}')
        
        self._is_assembly = (self._name, {'data': self._data, 'mime-type': self._mime_type})

        if self._template is not None:
            self._data = await render_pct_async(self._data, self._template._vars_backend)

            template = self._template.serialize()

            self._is_assembly[1]['templates'] = template

    
        return self._is_assembly
        







class GNRequest:
    def __init__(
        self,
        method: str,
        url: Url,
        payload: Optional[dict] = None, # msgpack object
        cookies: Optional[dict] = None, # передаются один раз. сохраняются на сервере в сессии,
        gn_protocol: Optional[str] = None,
        route: Optional[str] = None,
        stream: bool = False,
        origin: Optional[str] = None
    ):
        self._method = method
        self._url = url
        self._payload = payload
        self._cookies = cookies
        self._gn_protocol = gn_protocol
        self._route = route
        self._stream = stream
        self._origin = origin

        self._url.method = method

        self.user = self.__user(self)

    class __user:
        def __init__(self, request: GNRequest) -> None:
            self.__request = request
            self._data = {}
        
        @property
        def gwisid(self) -> int:
            """
            # ID объекта

            Возвращает уникальный идентификатор объекта в системе GW

            Этот идентификатор используется для управления объектами в системе.

            Может использоваться для идентификации пользователя.
            
            :return: int
            """
            return self._data.get("gwisid", 0)
        
        @property
        def sessionId(self) -> int:
            """
            # ID сессии

            Возвращает уникальный идентификатор сессии пользователя в сети GN.
            
            Этот идентификатор используется для отслеживания состояния сессии пользователя в системе.

            Может использоваться для идентификации пользователя.
            
            :return: int
            """
            return self._data.get("session_id", 0)
        
        @property
        def nickname(self) -> str:
            """
            # Никнейм объекта

            Возвращает никнейм объекта в системе GW.

            Никнейм используется для идентификации объекта в системе пользователями.

            Может использоваться для идентификации пользователя.

            :return: str
            """
            return self._data.get("nickname", "")

        @property
        def objectType(self) -> int:
            """
            # Тип объекта

            Возвращает тип объекта в системе GW.
            
            Тип объекта используется для определения роли и функциональности объекта в системе.

            Может использоваться для идентификации пользователя.

            Возможные значения:
            - 2: Пользователь
            - 3: Компания
            - 4: Проект
            - 5: Продукт

            :return: int
            """
            return self._data.get("object_type", 0)
        
        @property
        def viewingType(self) -> int:
            """
            # Тип просмотра

            Возвращает тип просмотра объекта в системе GW.
            Тип просмотра может быть установлен объекту для определения уровня доступа к объекту.

            Возможные значения:
            - 0: Просмотр доступен только владельцу объекта
            - 1: Просмотр не ограничен
            - 2: Просмотр только авторизованным пользователям
            - 3: Просмотр только для официально подтвержденных пользователей 

            :return: int
            """
            return self._data.get("viewing_type", 0)

        @property
        def description(self) -> str:
            """
            # Описание объекта

            Возвращает описание объекта в системе GW.
            Описание может содержать дополнительную информацию о объекте.

            :return: str
            """
            return self._data.get("description", "")

        @property
        def name(self) -> str:
            """
            # Имя объекта

            Возвращает имя объекта в системе GW.

            Имя НЕ может быть использовано для идентификации объекта в системе пользователями.

            Может использоваться для определения объекта только пользователями.

            :return: str
            """
            return self._data.get("name", "")
        
        @property
        def owner(self) -> Optional[int]:
            """
            # gwisid владельца объекта

            Возвращает уникальный идентификатор владельца объекта в системе GW.
            Этот идентификатор используется для определения владельца объекта.

            :return: Optional[int]
            Если владелец не установлен, возвращает None.
            """
            return self._data.get("owner", None)
        
        @property
        def officiallyConfirmed(self) -> bool:
            """
            # Официально подтвержденный объект

            Возвращает True, если объект официально подтвержден в системе GW.
            Официально подтвержденные объекты могут иметь дополнительные права и возможности.

            :return: bool
            """
            return self._data.get("of_conf", False)


    def serialize(self, mode: int = 0) -> bytes:
        if self._gn_protocol is None: self.setGNProtocol()
        if self._route is None: self.setRoute()
        d = {
            1: self._method,
            2: str(self._url),
            7: self._route,
            8: self._gn_protocol
        }
        
        if self._cookies is not None:
            d[4] = self._cookies
        if self._payload is not None:
            d[5] = self._payload
        if not mode:
            d[6] = self.stream
        if d[7] == 'gn:proxy:request-to-real-server':
            d[7] = True
        if self.user._data != {}:
            d[9] = self.user._data
        if self._origin is not None:
            d[10] = self._origin
        blob: bytes = msgpack.dumps(d, use_bin_type=True)
        return _pack(mode, self.stream, len(blob) + 8) + blob if mode else blob

    @staticmethod
    def deserialize(data: bytes, mode: int = 0) -> 'GNRequest':
        if mode:
            if len(data) < 8:
                raise Exception('len')
            _mode, stream, length = _unpack(data[:8])
            if _mode != mode:
                raise Exception('decrypt error')
            data = data[8:length]
        else:
            stream = None
        unpacked: dict = msgpack.loads(data, raw=False, strict_map_key=False)
        _url = Url(unpacked[2])
        if not _url.method:
            _url.method = unpacked[1]
        route_ = unpacked.get(7)
        if mode:
            if route_ is True:
                route_ = 'gn:proxy:request-to-real-server'
        

        r = GNRequest(
            method=unpacked[1],
            url=_url,
            payload=unpacked.get(5),
            cookies=unpacked.get(4),
            stream=stream if stream is not None else unpacked.get(6),
            gn_protocol=unpacked.get(8),
            route=route_,
            origin=unpacked.get(10)
        )
        r.user._data = unpacked.get(9)
        return r
    @staticmethod
    def type(data: bytes) -> Tuple[int, bool, int]:
        return _unpack(data)

    @property
    def method(self) -> str:
        """
        Метод запроса (GET, POST, PUT, DELETE и т.д.)
        """
        return self._method
    
    def setMethod(self, method: str):
        """
        Устанавливает метод запроса.
        :param method: Метод запроса (GET, POST, PUT, DELETE и т.д.)
        """
        self._method = method
        self._url.method = method
    
    @property
    def url(self) -> Url:
        """
        Возвращает URL запроса.
        """
        return self._url

    def setUrl(self, url: Url):
        """
        Устанавливает URL запроса.
        :param url: URL запроса в виде объекта Url.
        """
        self._url = url

    @property
    def payload(self) -> Optional[dict]:
        """
        Возвращает полезную нагрузку запроса.

        Dict с поддержкой байтов.
        Если полезная нагрузка не установлена, возвращает None.
        """
        return self._payload

    def setPayload(self, payload: dict):
        """
        Устанавливает полезную нагрузку запроса.
        :param payload: Dict с поддержкой байтов.
        """
        self._payload = payload

    @property
    def cookies(self) -> Optional[dict]:
        return self._cookies

    def setCookies(self, cookies: dict):
        self._cookies = cookies
        

    @property
    def gn_protocol(self) -> Optional['GNProtocol']:
        """
        Возвращает GN протокол

        GN протокол используется для подключения к сети GN.
        Если протокол не установлен, возвращает None.
        """
        return GNProtocol(self._gn_protocol) if self._gn_protocol else None

    @property
    def gn_protocol_str(self) -> Optional[str]:
        """
        Возвращает GN протокол в виде строки.
        Если GN протокол не установлен, возвращает None.
        """
        return self._gn_protocol
    
    def setGNProtocol(self, gn_protocol: Optional[str] = None):
        """
        Устанавливает GN протокол.
        :param gn_protocol: GN протокол (например, 'gn:tcp:0.1', 'gn:quic',..).
        Если не указан, используется 'gn:quic:real'.
        """
        if gn_protocol is None:
            gn_protocol = 'gn:quic:real'
        self._gn_protocol = gn_protocol

    @property
    def route(self) -> Optional[str]:
        """
        Возвращает маршрут запроса.
        Маршрут используется для определения конечной точки запроса в сети GN.
        Если маршрут не установлен, возвращает None.
        """
        return self._route
    
    def setRoute(self, route: Optional[str] = None):
        """
        Устанавливает маршрут запроса.
        :param route: Маршрут запроса (например, 'gn:proxy:request-to-real-server').
        Если не указан, используется 'gn:proxy:request-to-real-server'.
        """
        if route is None:
            route = 'gn:proxy:request-to-real-server'
        self._route = route

    @property
    def stream(self) -> bool:
        return self._stream

    def __repr__(self):
        return f"<GNRequest [{self._method} {self._url}] [{self._gn_protocol}]>"
    
class GNResponse:
    def __init__(self, command: str, payload: Optional[dict] = None, files: Optional[Union[str, FileObject,  List[FileObject]]] = None, cors: Optional[CORSObject] = None):
        self._command = command
        self._payload = payload
        self._stream = False
        self._cors = cors

        self._files = files

    async def assembly(self) -> GNResponse:
        """
        Сборка ответа в формат gn для отправки
        """

        if self._files is not None:
            _files = {}
            if not isinstance(self._files, list):
                self._files = {0:self._files}

            if isinstance(self._files, dict):
                for file in self._files.values():
                    if not isinstance(file, dict):
                        if isinstance(file, str):
                            file = FileObject(file)

                        name, assembly_file = await file.assembly()
                        _files[name or 0] = assembly_file

            self._files = _files


        return self

    def serialize(self, mode: int = 0) -> bytes:
        d = {
            1: self._command
        }

        if d[1] == 'ok':
            d[1] = True

        if self._payload is not None:
            d[2] = self._payload

        if not mode:
            d[3] = self.stream
        
        if self._cors is not None:
            d[4] = self._cors.serialize()

        if self._files:
            d[5] = self._files


        blob: bytes = msgpack.dumps(d, use_bin_type=True)
        return _pack(mode, self.stream, len(blob) + 8) + blob if mode else blob
    
    @staticmethod
    def deserialize(data: bytes, mode: int = 0) -> 'GNResponse':
        if mode:
            if len(data) < 8:
                raise Exception('len')
            
            _mode, stream, length = _unpack(data[:8])

            if _mode != mode:
                raise Exception('decrypt error')

            data = data[8:length]
        else:
            stream = None

                

        unpacked: Dict = msgpack.loads(data, raw=False, strict_map_key=False)

        cm = unpacked.get(1)
        if cm is True:
            cm = 'ok'

        r = GNResponse(
            command=unpacked.get(1, 'gn:no-command'),
            payload=unpacked.get(2),
            cors=CORSObject.deserialize(unpacked[4]) if 4 in unpacked else None

        )
        r._stream = stream if stream is not None else unpacked.get(3)
        r._files = unpacked.get(5)
        return r
    
    @staticmethod
    def type(data: bytes) -> Tuple[int, bool, int]:
        return _unpack(data)

    @property
    def command(self) -> str:
        return self._command

    @property
    def payload(self) -> Optional[dict]:
        return self._payload
    
    @property
    def stream(self) -> bool:
        return self._stream
    
    def __repr__(self):
        return f"<GNResponse [{self._command} {len(self._payload) if self._payload else ''}]>"

_VERSION_RE = re.compile(r"^\d+(?:\.\d+)*(?:-\d+(?:\.\d+)*)?$").match
_is_ver = _VERSION_RE


def _to_list(v: str) -> List[int]:
    return [int(x) for x in v.split(".")] if v else []


def _cmp(a: List[int], b: List[int]) -> int:
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return (a > b) - (a < b)



class _VersionRange:
    """Одиночная версия, диапазон a‑b, 'last' или wildcard (None)."""

    __slots__ = ("raw", "kind", "lo", "hi", "single")

    def __init__(self, raw: Optional[str]):
        self.raw = raw             # None == wildcard
        if raw is None:
            self.kind = "wild"
            return
        if raw.lower() == "last":
            self.kind = "single_last"
            return
        if "-" in raw:
            self.kind = "range"
            lo, hi = raw.split("-", 1)
            self.lo = _to_list(lo)
            self.hi = _to_list(hi)
        else:
            self.kind = "single"
            self.single = _to_list(raw)

    def contains(self, ver: Optional[str]) -> bool:  # noqa: C901
        if self.kind == "wild":
            return True
        ver = ver or "last"
        if self.kind == "single_last":
            return ver.lower() == "last"
        if ver.lower() == "last":
            return False
        v = _to_list(ver)
        if self.kind == "single":
            return _cmp(self.single[:], v) == 0
        return _cmp(self.lo[:], v) <= 0 <= _cmp(v, self.hi[:])

    # for debugging / logs
    def __str__(self) -> str:
        return self.raw or "last"


class _Pat(NamedTuple):
    gn_ver: _VersionRange
    p1_name: Optional[str]
    p1_ver: _VersionRange
    p1_need_last: bool
    p2_name: Optional[str]
    p2_ver: _VersionRange
    p2_need_last: bool


@lru_cache(maxsize=2048)
def _compile_full_pattern(pat: str) -> _Pat:
    t = pat.split(":")
    gn_ver = _VersionRange(None)
    if t and t[0].lower() == "gn":
        t.pop(0)
        gn_ver = _VersionRange(t.pop(0)) if t and (_is_ver(t[0]) or t[0].lower() == "last") else _VersionRange(None)

    p2_name = p2_ver = p1_name = p1_ver = None
    p2_need_last = p1_need_last = False

    if t:
        if _is_ver(t[-1]) or t[-1].lower() == "last":
            p2_ver = _VersionRange(t.pop())
        else:
            p2_need_last = True
        p2_name = t.pop() if t else None

    if t:
        if _is_ver(t[-1]) or t[-1].lower() == "last":
            p1_ver = _VersionRange(t.pop())
        else:
            p1_need_last = True
        p1_name = t.pop() if t else None

    if t:
        raise ValueError(f"bad pattern {pat!r}")

    return _Pat(
        gn_ver=gn_ver,
        p1_name=None if p1_name is None else p1_name.lower(),
        p1_ver=p1_ver or _VersionRange(None),
        p1_need_last=p1_need_last,
        p2_name=None if p2_name is None else p2_name.lower(),
        p2_ver=p2_ver or _VersionRange(None),
        p2_need_last=p2_need_last,
    )


class _LeafPat(NamedTuple):
    name: Optional[str]
    ver: _VersionRange
    need_last: bool


@lru_cache(maxsize=4096)
def _compile_leaf_pattern(pat: str) -> _LeafPat:
    """
    pattern ::= NAME
              | NAME ':' VERSION
              | VERSION             (# имя опущено)
    """
    if ":" not in pat:
        if _is_ver(pat) or pat.lower() == "last":
            return _LeafPat(name=None, ver=_VersionRange(pat), need_last=False)
        return _LeafPat(name=pat.lower(), ver=_VersionRange(None), need_last=True)

    name, ver = pat.split(":", 1)
    name = name.lower() or None
    need_last = False
    if not ver:
        need_last = True
        ver_range = _VersionRange(None)
    else:
        ver_range = _VersionRange(ver)
    return _LeafPat(name=name, ver=ver_range, need_last=need_last)


# ────────────────── main class ────────────────────────────────────────────────
class GNProtocol:
    """
    Строка формата  gn[:gnVer]:connection[:ver1]:route[:ver2]
    """

    __slots__ = (
        "raw",
        "gn_ver_raw",
        "gn_ver",
        "conn_name",
        "conn_ver_raw",
        "conn_ver",
        "route_name",
        "route_ver_raw",
        "route_ver",
        "_gn_leaf",
        "_conn_leaf",
        "_route_leaf",
    )

    # ---------------------------------------------------------------- init ---
    def __init__(self, raw: str):
        self.raw = raw
        self._parse()
        self._gn_leaf = self._LeafProto("gn", self.gn_ver_raw)
        self._conn_leaf = self._LeafProto(self.conn_name, self.conn_ver_raw)
        self._route_leaf = self._LeafProto(self.route_name, self.route_ver_raw)

    # ---------------------------------------------------------------- parse --
    @staticmethod
    def _take_ver(tokens: List[str]) -> Optional[str]:
        return tokens.pop(0) if tokens and (_is_ver(tokens[0]) or tokens[0].lower() == "last") else None

    def _parse(self) -> None:
        t = self.raw.split(":")
        if not t or t[0].lower() != "gn":
            raise ValueError("must start with 'gn'")
        t.pop(0)

        self.gn_ver_raw = self._take_ver(t)
        self.gn_ver = _VersionRange(self.gn_ver_raw)

        if not t:
            raise ValueError("missing connection proto")
        self.conn_name = t.pop(0).lower()
        self.conn_ver_raw = self._take_ver(t)
        self.conn_ver = _VersionRange(self.conn_ver_raw)

        if not t:
            raise ValueError("missing route proto")
        self.route_name = t.pop(0).lower()
        self.route_ver_raw = self._take_ver(t)
        self.route_ver = _VersionRange(self.route_ver_raw)

        if t:
            raise ValueError(f"extra tokens: {t!r}")

    def structure(self) -> dict:
        return {
            "gn": {"version": str(self.gn_ver)},
            self.conn_name: {"version": str(self.conn_ver)},
            self.route_name: {"version": str(self.route_ver)},
        }

    def matches_any(self, patterns: Iterable[str]) -> bool:
        gv = self.gn_ver_raw
        c_name, c_ver = self.conn_name, self.conn_ver_raw
        r_name, r_ver = self.route_name, self.route_ver_raw

        for pat in patterns:
            gn_v, p1n, p1v, p1need, p2n, p2v, p2need = _compile_full_pattern(pat)

            # gn
            if not gn_v.contains(gv):
                continue

            # connection
            if p1n and p1n != c_name:
                continue
            if p1need:
                if c_ver is not None:
                    continue
            elif not p1v.contains(c_ver):
                continue

            # route
            if p2n and p2n != r_name:
                continue
            if p2need:
                if r_ver is not None:
                    continue
            elif not p2v.contains(r_ver):
                continue

            return True
        return False

    class _LeafProto:
        __slots__ = ("_name", "_ver_raw")

        def __init__(self, name: str, ver_raw: Optional[str]):
            self._name = name
            self._ver_raw = ver_raw  # None == 'last'

        def protocol(self) -> str:
            return self._name

        def version(self) -> str:
            return self._ver_raw or "last"

        def matches_any(self, *patterns) -> bool:
            if len(patterns) == 1 and not isinstance(patterns[0], str):
                patterns_iter = patterns[0]
            else:
                patterns_iter = patterns

            nm = self._name
            vr = self._ver_raw

            for p in patterns_iter:
                pat = _compile_leaf_pattern(p)

                if pat.name is not None and pat.name != nm:
                    continue

                if pat.need_last:
                    if vr is not None:
                        continue
                    return True

                if pat.ver.contains(vr):
                    return True

            return False

        def __repr__(self) -> str:
            return f"<Proto {self._name}:{self.version()}>"

    @property
    def gn(self) -> _LeafProto:
        """Top‑level 'gn' protocol."""
        return self._gn_leaf

    @property
    def connection(self) -> _LeafProto:
        return self._conn_leaf

    @property
    def route(self) -> _LeafProto:
        return self._route_leaf

    def __repr__(self) -> str:
        return (
            f"<GNProtocol gn:{self.gn_ver_raw or 'last'} "
            f"{self.conn_name}:{self.conn_ver_raw or 'last'} "
            f"{self.route_name}:{self.route_ver_raw or 'last'}>"
        )
