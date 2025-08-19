"""
GW Client
~~~~~~~~~

 - mmbp

 - mmbps

*created by KeyisB*

-==============================-




Copyright (C) 2024 KeyisB. All rights reserved.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to use the Software exclusively for
projects related to the MMB or GW systems, including personal,
educational, and commercial purposes, subject to the following
conditions:

1. Copying, modification, merging, publishing, distribution,
sublicensing, and/or selling copies of the Software are
strictly prohibited.
2. The licensee may use the Software only in its original,
unmodified form.
3. All copies or substantial portions of the Software must
remain unaltered and include this copyright notice and these terms of use.
4. Use of the Software for projects not related to GW or
MMB systems is strictly prohibited.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR
A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
__GW_VERSION__ = "0.0.0.0.4"
__version__ = "1.4.0.1.25"

__all__ = [
    "AsyncClient",
    "Client",
    "ProtocolsManager",
    "Url",
    "DNS",
    "DNSObject",
    "Exceptions",
    "Request",
    "Response",
    "ssl_gw_crt_path"
]

from .core import (
    Url,
    DNS,
    DNSObject,
    ProtocolsManager
    )
from .Clients import AsyncClient, Client
from .models import Request, Response
from .Exceptions import Exceptions
from .dnsCore import ssl_gw_crt_path




import KeyisBClient_httpx as httpx
ProtocolsManager.addClient(httpx.Client()) # type: ignore

import KeyisBClient_mmbp as mmbp
ProtocolsManager.addClient(mmbp.Client()) # type: ignore

from .gw_certs import *











