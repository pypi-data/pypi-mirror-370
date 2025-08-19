import httpx
import os

import os
import sys

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS # type: ignore
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

paths = [
    "C:/GW/certificates/ssl",
    resource_path('KeyisBClient/gw_certs'),
    resource_path('gw_certs')
]

for path in paths:
    ssl_gw_crt_path = path + '/v0.0.1.crt'
    #print(f'SSL certificate for GW at: {ssl_gw_crt_path} [{os.path.exists(ssl_gw_crt_path)}]')
    if os.path.exists(ssl_gw_crt_path):
        break

if not os.path.exists(ssl_gw_crt_path):
    ssl_gw_crt_path = ssl_gw_crt_path.replace('\\', '/')
    os.makedirs('/'.join(ssl_gw_crt_path.split('/')[:-1]), exist_ok=True)
    open(ssl_gw_crt_path, 'w').write("""
-----BEGIN CERTIFICATE-----
MIIDszCCApugAwIBAgIUIEUvi2bdBH5yNb2Qi75IqGqMd7wwDQYJKoZIhvcNAQEL
BQAwYTELMAkGA1UEBhMCVVMxDjAMBgNVBAgMBVN0YXRlMQ0wCwYDVQQHDARDaXR5
MRUwEwYDVQQKDAxPcmdhbml6YXRpb24xDTALBgNVBAsMBFVuaXQxDTALBgNVBAMM
BE15Q0EwHhcNMjUwNTA1MDEwMTExWhcNMzUwNTAzMDEwMTExWjBhMQswCQYDVQQG
EwJVUzEOMAwGA1UECAwFU3RhdGUxDTALBgNVBAcMBENpdHkxFTATBgNVBAoMDE9y
Z2FuaXphdGlvbjENMAsGA1UECwwEVW5pdDENMAsGA1UEAwwETXlDQTCCASIwDQYJ
KoZIhvcNAQEBBQADggEPADCCAQoCggEBAMbDdWyR5n3qKaYkZvkiXtVJ7DekJn6Q
eJA+kvje4KzxBlD+SkdkYMQxuTVU2yuNYXX88LhSbPygrzFSU7q3HG9dNwonWwP6
05XFAvYZ5LDNI7DrjRecE/+JvpgXaAwcv3IJRpuJU1e+JL2K3Z9wwhxYEJM+N/aN
pP8Zyr5ktXJgEKhWOVtpj2LSXno33SI04B0LWVlbiZX/yWtK3X/BJPlXaMn+r76n
6L3JDNSjtuBGqSI7FHDQEPd3dcsdK6SbP6ORndp72EZfLcJbyXLtYdHgjJS9DrD4
0f5Laq2SQ2oo/B3MKNNF/Y8e1USX1tIe+lePmqzjJJk2oB1GSBiaX00CAwEAAaNj
MGEwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYEFM8O
S2OUe3Xkh7XkQ95s+MZTCtsuMB8GA1UdIwQYMBaAFM8OS2OUe3Xkh7XkQ95s+MZT
CtsuMA0GCSqGSIb3DQEBCwUAA4IBAQA3OwR0e9rPAgQ3nIHJrs+Tm7xr5DFAigd0
V13Klncrl7SPD0HrqQ88qNhHZcXJqy8Y6y3sUIknisud+9cnzYo/rNgpSG702ZAo
D/+ILHV51D8OZssoBaAWTfMA/NchPRXGDGJ5vBG/nXgvdpVdRnDepspKY1rYYTV0
JYZ99+nSa3eyDQxyMmYSzK0hQmKHdJEMkb8Es2/hRlAktL31irlXW15Fr3li5pmj
jRIER3q1T4WNyIuBRdNKYi03Eh342RWgl6C5Yjs1WBXsSXMhKpEw3Hlkc973CWb0
oKCo/cPl0mNfdrj5ER3njUOvItIpPAOajqVN9RsALSc0jC9M8pWJ
-----END CERTIFICATE-----
""")


class __DNSCore:
    def __init__(self) -> None:
        #from KeyisBLogging import logging
        #logging.error('\n' + '='*50 +  '\n              CLIENT STARTED\n' + '='*50)
        try:
            if os.path.exists(ssl_gw_crt_path):
                self._connectionAsync = httpx.AsyncClient(verify=ssl_gw_crt_path)
                self._connectionSync = httpx.Client(verify=ssl_gw_crt_path)
                self.hosts = [
                        {'host': 'http://51.250.85.38:50000', 'status': 'unknown', 'add_type': 'main'},
                        {'host': 'http://api.dns.gw.mmbproject.com:50000', 'status': 'unknown', 'add_type': 'main'},
                ]
                self.checkForAnyDNSHosts()
        except Exception as e:
            print(e)
    def checkForAnyDNSHosts(self):
        path = "C:/GW/DNS/hosts.txt"
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            self.hosts.append({
                                'host': line,
                                'status': 'unknown',
                                'add_type': 'outFile'
                                })
            except: pass
DNSCore = __DNSCore()