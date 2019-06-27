# -*- coding: utf-8 -*-
import time
import json
import datetime
import chardet
from pprint import pprint
from http import HTTPStatus

import requests
import chardet
from bs4 import BeautifulSoup as BS
from colorama import Fore
from lxml import etree

import config


def print_message(msg, *args, **kwargs):
    color = kwargs.pop('color', Fore.LIGHTGREEN_EX)
    print(color + msg, *args, **kwargs)


def test_need_relogin(driver, tries=120):
    """
    Testea si se necesita hacer relogin en la pagina por que la cookie de sesion haya expirado/cerrado.
    :param driver: Instancia de WebDriver
    :return bool: True o False
    """
    jar = requests.cookies.RequestsCookieJar()
    for navcookie in driver.get_cookies():
        jar.set(navcookie.get('name'), navcookie.get('value'), domain=navcookie.get('domain'),
                path=navcookie.get('path'))

    for n in range(tries):
        try:
            resp = requests.get(
                url='https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/'
                    'registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
                cookies=jar,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                    'User-Agent': driver.execute_script('return window.navigator.userAgent;'),
                },
                allow_redirects=False,
                timeout=15,
            )
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
            print_message('\n[ERROR] - Error en utils.test_need_relogin: "{}"'.format(error), color=Fore.RED)
            time.sleep(10)
            continue
        else:
            if not resp.ok:
                print_message('[ERROR] - Error en utils.test_need_relogin, el servidor a devuelto el error: %d - %s'
                      % (resp.status_code, resp.reason), color=Fore.RED)
                time.sleep(10)
                continue
            
            return resp.status_code == HTTPStatus.FOUND
    
    return False


def get_login_new_cookie(cookies=None, user_agent='Mozilla/5.0', tries=120):
    """
    Hace una peticion post a "https://mexitel.sre.gob.mx/citas.webportal/pages/public/login/j_security_check" 
    para logearse nuevamente sin hacerlo mediante el navegador.
    """
    url_post = 'https://mexitel.sre.gob.mx/citas.webportal/pages/public/login/j_security_check'
    for n in range(tries):
        print_message('[INFO] - Intento de relogin: %d de %d...\t\t' % (n, tries), end='\r')
        try:
            resp_get = requests.get(
                # url=config.LOGIN_URL,
                url='{}?_={}'.format(config.LOGIN_URL, int(datetime.datetime.now().timestamp())),
                cookies=cookies,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                    'User-Agent': user_agent,
                    'Cache-Control': 'no-cache, max-age=0',
                    'Pragma': 'no-cache',
                },
                allow_redirects=True,
                timeout=60,
            )
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
            print_message('\n[ERROR] - Error en relogin, obtencion de pagina de login: "{}"'.format(error), color=Fore.RED)
            time.sleep(10)
            continue
        else:
            if not resp_get.ok:
                print_message('\n[ERROR] - Error al obtener pagina de login: %d - %s' % (resp_get.status_code, resp_get.reason),
                              color=Fore.RED)
                time.sleep(10)
                continue

            try:
                # print('Cookies resp_get:', resp_get.cookies)
                # print(url_post)
                # print(user_agent)
                # print(config.USERNAME)
                # print(config.PASSWORD)
                resp_post = requests.post(
                    # url=url_post,
                    url='{}?_={}'.format(url_post, int(datetime.datetime.now().timestamp())),
                    data={
                        'j_username': config.USERNAME,
                        'j_password': config.PASSWORD,
                    },
                    cookies=resp_get.cookies,
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,'
                                  'image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': user_agent,
                        'Origin': 'https://mexitel.sre.gob.mx',
                        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/public/login/login.jsf',
                        'Cache-Control': 'no-cache, max-age=0',
                        'Pragma': 'no-cache',
                    },
                    allow_redirects=False,
                    timeout=60,
                )
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
                print_message('\n[ERROR] - Error en relogin, peticion POST: "{}"'.format(error), color=Fore.RED)
                time.sleep(10)
                continue
            else:
                print()
                if not resp_post.ok:
                    print_message('[ERROR] - Error en peticion POST relogin, el servidor a devuelto el error: %d - %s'
                          % (resp_post.status_code, resp_post.reason), color=Fore.RED)
                    time.sleep(10)
                    continue
                
                if resp_post.status_code != HTTPStatus.FOUND:   # 302
                    print_message('[ERROR] - Error en relogin, el servidor a devuelto el codigo %d se esparaba 302'
                          % resp_post.status_code, color=Fore.RED)
                    time.sleep(10)
                    continue

                # print('Cookies resp_post:', resp_post.cookies)

                # Hacemos la peticion para obtener nuevo javax.faces.ViewState
                try:
                    url_get = 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/' \
                              'registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true'
                    resp3 = requests.get(
                        url='{}&_={}'.format(url_get, int(datetime.datetime.now().timestamp())),
                        cookies=resp_post.cookies,
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                                      'image/webp,image/apng,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                            'User-Agent': user_agent,
                            'Cache-Control': 'no-cache, max-age=0',
                            'Pragma': 'no-cache',
                        },
                        allow_redirects=True,
                        timeout=60,
                    )
                except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) \
                        as error:
                    print_message('[ERROR] - Error en relogin, obteniendo pagina de citas: "{}"'.format(error), color=Fore.RED)
                    time.sleep(10)
                    continue
                else:
                    if not resp3.ok:
                        print_message('[ERROR] - Error obteniendo javax.faces.ViewState, el servidor a respondido: %d - %s'
                              % (resp3.status_code, resp3.reason), color=Fore.RED)
                        time.sleep(10)
                        continue

                    # Utilizamos BS
                    encoding = chardet.detect(resp3.content).get('encoding', 'UTF-8')
                    content = resp3.content.decode(encoding)
                    soup = BS(content, "lxml")
                    el = soup.find('input', attrs={'name': 'javax.faces.ViewState', 'type': 'hidden'})
                    if not el:
                        print_message('[ERROR] - No se puede encontrar el elemento input[name="javax.faces.ViewState"]', color=Fore.RED)
                        time.sleep(10)
                        continue
                    
                print_message('[INFO] - Relogin satifactorio')
                return resp_post.cookies, el['value']
    
    return None, None


def relogin(driver):
    ua = driver.execute_script('return window.navigator.userAgent;')

    # jar = requests.cookies.RequestsCookieJar()
    # for navcookie in driver.get_cookies():
    # jar.set(navcookie.get('name'), navcookie.get('value'), domain=navcookie.get('domain'),
    # path=navcookie.get('path'))
    
    # WARN: No se estan pasando las cookies del navegador a get_login_new_cookie
    new_cookies, view_state = get_login_new_cookie(user_agent=ua)
    if not new_cookies:
        return False

    # Estableciendo las nuevas cookies
    for cookie in new_cookies:
        print_message('[INFO] - Estableciendo cookie {}: {}'.format(cookie.name, cookie.value))
        driver.delete_cookie(cookie.name)
        cdict = {
            'name': cookie.name, 'value': cookie.value, 
            'path': cookie.path, 'domain': cookie.domain, 
            'secure': cookie.secure, 'expiry': cookie.expires,
        }
        driver.add_cookie(cdict)
    
    # Estableciendo el nuevo ViewState
    if not driver.find_elements_by_name('javax.faces.ViewState'):
        print_message('[ERROR] - No se encontraron elementos del ViewState', color=Fore.RED)
        return False

    print_message('[INFO] - Estableciendo nuevo javax.faces.ViewState:', view_state)
    driver.execute_script("""\
    document.querySelectorAll('input[name="javax.faces.ViewState"]').forEach((e, i) => { e.value="%s" })
    """ % view_state)
    
    time.sleep(0.5)
    
    return True


def parse_calendar_data_month(xml: bytes) -> dict:
    """
    Parsea el XML de la respuesta a obtencion de eventos de calendario en modo mes.
    :param xml: String con XML
    :return: Diccionario(JSON) con datos de calendario o None en caso de error
    """
    parser = etree.XMLParser(load_dtd=False, no_network=True, ns_clean=True, remove_comments=True)
    try:
        root = etree.fromstring(xml, parser)
    except etree.ParseError as error:
        print_message('[ERROR] - Parseando respuesta XML en utils.parse_calendar_data_month: "{}"'.format(error),
                      color=Fore.RED)
        return None
    else:
        xpath = '/partial-response/changes/update[@id="formRegistroCitaExtranjero:schedule"]'
        el = root.xpath(xpath)
        if not el:
            print_message('[ERROR] - No se encuentra el XPath "{}" en utils.parse_calendar_data_month'.format(xpath),
                          color=Fore.RED)
            return None
    
        el = el[0]
        try:
            data = json.loads(el.text)
        except json.JSONDecodeError as error:
            print_message('[ERROR] - JSON de datos de calendario invalidos: {}'.format(error))
            return None
        
        assert 'events' in data
        for event in data['events']:
            for key in ['allDay', 'className', 'editable', 'end', 'id', 'start', 'title']:
                assert key in event, 'No existe "{}" en evento de calendario: {}'.format(key, event)
    
            # 2019-06-28T09:30:00-0500
            try:
                event['start'] = datetime.datetime.strptime(event.get('start'), '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                print_message('[WARN] - No se puede interpretar la fecha '
                              'en campo "start" en evento de calendario: {}'.format(event.get('start')))
                return None
            
            try:
                event['end'] = datetime.datetime.strptime(event.get('end'), '%Y-%m-%dT%H:%M:%S%z')
            except ValueError:
                print_message('[WARN] - No se puede interpretar la fecha '
                              'en campo "end" en evento de calendario: {}'.format(event.get('end')))
                return None

        return data


def response_to_file(response: requests.Response) -> None:
    """
    Registra todas las peticiones a fichero de logs
    :param response: Instancia de requests.Response
    :return: None
    """
    with open(config.REQUEST_LOG_FILE, 'a') as fd:
        request = response.request
        print('{}'.format(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')), file=fd)
        print('%s %s' % (request.method, request.url), file=fd)
        print(file=fd)
        pprint(request.headers, stream=fd)
        print(file=fd)
        pprint(request.body, stream=fd)
        print('\n', file=fd)
        print(response.status_code, response.reason, file=fd)
        pprint(response.headers, stream=fd)
        print('\n', file=fd)
        enconding = chardet.detect(response.content).get('encoding', 'UTF-8')
        print(response.content.decode(encoding=enconding), file=fd)
        print('\n\n%s\n\n' % ('=' * 130), file=fd)


if __name__ == '__main__':
    xml = b"""<?xml version='1.0' encoding='UTF-8'?>\
    <partial-response><changes><update id="formRegistroCitaExtranjero:schedule"><![CDATA[{"events" : [{"id": "4d5720ca-4452-4e76-b0d1-d59c0241d753","title": "No disponibles","start": "2019-06-10T00:00:00-0500","end": "2019-06-10T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "519c24ff-269e-420e-844b-5a4c59c68b2d","title": "No disponibles","start": "2019-06-11T00:00:00-0500","end": "2019-06-11T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "00962c4c-7515-4ae2-b4cf-c1783b13fc38","title": "No disponibles","start": "2019-06-12T00:00:00-0500","end": "2019-06-12T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "5962a849-af95-453b-8de4-bec61baaa43f","title": "No disponibles","start": "2019-06-13T00:00:00-0500","end": "2019-06-13T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "3e114b30-7e20-48f2-83a4-7615dc862a00","title": "No disponibles","start": "2019-06-14T00:00:00-0500","end": "2019-06-14T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "f2c49ee0-4619-486b-8307-b359e49f08b3","title": "No disponibles","start": "2019-06-17T00:00:00-0500","end": "2019-06-17T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "2a801c93-4188-4b63-83bf-2cd6a21ddb1b","title": "No disponibles","start": "2019-06-18T00:00:00-0500","end": "2019-06-18T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "14c4ef31-871b-4c2d-a666-9ee9f2ec7447","title": "No disponibles","start": "2019-06-19T00:00:00-0500","end": "2019-06-19T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "f55a57f4-c512-4306-819f-f30a57309b31","title": "No disponibles","start": "2019-06-20T00:00:00-0500","end": "2019-06-20T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "09231607-6dbd-48c1-9400-9a778ed95f73","title": "No disponibles","start": "2019-06-21T00:00:00-0500","end": "2019-06-21T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "eb4b42ec-ca8d-4b9c-8c59-ff980790272d","title": "No disponibles","start": "2019-06-24T00:00:00-0500","end": "2019-06-24T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "53d74b95-dc7b-41e6-a347-41b67ecce4bd","title": "No disponibles","start": "2019-06-25T00:00:00-0500","end": "2019-06-25T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "ff5bfafe-9756-4aa2-aedc-1442fcb3f2bb","title": "No disponibles","start": "2019-06-26T00:00:00-0500","end": "2019-06-26T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "15719898-5d3b-42c6-b6e7-6c15134ca7e0","title": "No disponibles","start": "2019-06-27T00:00:00-0500","end": "2019-06-27T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"},{"id": "3b1be618-1df6-4a9d-884a-311d9099c4f4","title": "No disponibles","start": "2019-06-28T00:00:00-0500","end": "2019-06-28T23:59:00-0500","allDay":true,"editable":true,"className":"rangoSaturado"}]}]]></update><update id="javax.faces.ViewState"><![CDATA[325560767426099253:6143328538903944043]]></update></changes></partial-response>
    """
    print(parse_calendar_data_month(xml))