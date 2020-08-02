# -*- coding: utf-8 -*-
import argparse

import requests
from colorama import Fore

import utils


def parse_argument() -> argparse.Namespace:
    """
    Parsea los parametros de la linea de comandos
    :return: Instancia de argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='CFUID cookies getter')
    parser.add_argument('-c', nargs=1, type=int, required=True, choices=[1, 10, 100, 200, 300], help='Numero de cookies CFUID a obtener.')
    # parser.add_argument('file', nargs=1, help='Fichero con datos de clientes.')
    return parser.parse_args()


def main():
    args = parse_argument()
    cfuid_count = args.c[0]
    
    url = 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf'

    with open('cfuid_cookies.txt', 'w') as fd:
        for n in range(cfuid_count):
            utils.print_message('[INFO] - Peticion %d de %d' % (n+1, cfuid_count), color=Fore.RESET)
            
            try:
                resp = requests.get(
                    url=url,
                    headers={
                        'Accept': 'text/html, application/xml, text/xml, */*; q=0.01',
                        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'User-Agent': 'Mozilla/5.0 Gecko/20100101 Firefox/65.0',
                        'Cache-Control': 'no-cache, max-age=0',
                        'Pragma': 'no-cache',
                    },
                    allow_redirects=False,
                    timeout=60,
                )
            except requests.Timeout:
                utils.print_message('[ERROR] - Tiempo de espera agotado en peticion', color=Fore.RED)
                continue
            except requests.ConnectionError as error:
                utils.print_message('[ERROR] - Error de conexion: "{}"'.format(error), color=Fore.RED)
                continue
            except requests.HTTPError as error:
                utils.print_message('[ERROR] - Error HTTP: "{}"'.format(error), color=Fore.RED)
                continue
            except requests.RequestException as error:
                utils.print_message('[ERROR] - Error en peticion: "{}"'.format(error), color=Fore.RED)
                continue
            else:
                assert resp.status_code == 302
                # print(resp.status_code)
                # print(resp.headers, '\n')
                # print(resp.cookies, '\n')
                # print(resp.raw.headers, '\n')
                for cookie in resp.cookies:
                    if cookie.name == '__cfduid':
                        fd.write('%s\n' % cookie.value)
                        print(cookie, cookie.expires, cookie.discard)


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        exit(0)
