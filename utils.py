# -*- coding: utf-8 -*-
import re
import time
from http import HTTPStatus

import requests
import chardet
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as BS

import config


def test_need_relogin(driver, tries=120):
    """
    Testea si se necesita hacer relogin en la pagina por que la cookie de sesion haya expirado/cerrado.
    :param driver: Instancia de WebDriver
    :return bool: True o False
    """
    jar = requests.cookies.RequestsCookieJar()
    for navcookie in driver.get_cookies():
        jar.set(navcookie.get('name'), navcookie.get('value'), domain=navcookie.get('domain'), path=navcookie.get('path'))

    for n in range(tries):
        try:
            resp = requests.get(
                url='https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
                cookies=jar,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                    'User-Agent': driver.execute_script('return window.navigator.userAgent;'),
                },
                allow_redirects=False,
                timeout=10,
            )
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
            print('\n[ERROR] - Error en utils.test_need_relogin: "{}"'.format(error))
            time.sleep(5)
            continue
        else:
            if not resp.ok:
                print('[ERROR] - Error en utils.test_need_relogin, el servidor a devuelto el error: %d - %s' % (resp.status_code, resp.reason))
                time.sleep(5)
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
        print('[INFO] - Intento de relogin: %d de %d...\t\t' % (n, tries), end='\r')
        try:
            resp_get = requests.get(
                url=config.LOGIN_URL,
                cookies=cookies,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                    'User-Agent': user_agent,
                },
                allow_redirects=True,
                timeout=10,
            )
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
            print('\n[ERROR] - Error en relogin, obtencion de pagina de login: "{}"'.format(error))
            time.sleep(5)
            continue
        else:
            if not resp_get.ok:
                print('[ERROR] - Error al obtener pagina de login: %d - %s' % (resp_get.status_code, resp_get.reason))
                return (None, None)

            try:
                # print('Cookies resp_get:', resp_get.cookies)
                # print(url_post)
                # print(user_agent)
                # print(config.USERNAME)
                # print(config.PASSWORD)
                resp_post = requests.post(
                    url=url_post, 
                    data={
                        'j_username': config.USERNAME,
                        'j_password': config.PASSWORD,
                    },
                    cookies=resp_get.cookies,
                    headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                        'Cache-Control': 'max-age=0',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': user_agent,
                        'Origin': 'https://mexitel.sre.gob.mx',
                        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/public/login/login.jsf',
                    },
                    allow_redirects=False,
                    timeout=10,
                )
            except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
                print('\n[ERROR] - Error en relogin, peticion POST: "{}"'.format(error))
                time.sleep(5)
                continue
            else:
                print()
                if not resp_post.ok:
                    print('[ERROR] - Error en relogin, el servidor a devuelto el error: %d - %s' % (resp_post.status_code, resp_post.reason))
                    print(resp_post.content)
                    continue
                
                if resp_post.status_code != HTTPStatus.FOUND:   # 302
                    print('[ERROR] - Error en relogin, el servidor a devuelto el codigo %d se esparaba 302' % resp_post.status_code)
                    return (None, None)

                # print('Cookies resp_post:', resp_post.cookies)

                # Hacemos la peticion a
                # https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true
                # para obtener nuev javax.faces.ViewState
                try:
                    resp3 = requests.get(
                        url='https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
                        cookies=resp_post.cookies,
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
                            'User-Agent': user_agent,
                        },
                        allow_redirects=True,
                        timeout=10,
                    )
                except (requests.Timeout, requests.ConnectionError, requests.HTTPError, requests.TooManyRedirects) as error:
                    print('[ERROR] - Error en relogin, obteniendo pagina de citas: "{}"'.format(error))
                    time.sleep(5)
                    continue
                else:
                    if not resp3.ok:
                        print('[ERROR] - Error obteniendo javax.faces.ViewState, el servidor a respondido: %d - %s' % (resp3.status_code, resp3.reason))
                        return (None, None)

                    # Utilizamos BS
                    encoding = chardet.detect(resp3.content).get('encoding', 'UTF-8')
                    content = resp3.content.decode(encoding)
                    soup = BS(content, "lxml")
                    el = soup.find('input', attrs={'name': 'javax.faces.ViewState', 'type': 'hidden'})
                    if not el:
                        print('[ERROR] - No se puede encontrar el elemento input[name="javax.faces.ViewState"]')
                        return (None, None)
                    
                    print('javax.faces.ViewState', el['value'])

                return (resp_post.cookies, el['value'])
    
    return (None, None)


def relogin(driver):
    ua = driver.execute_script('return window.navigator.userAgent;')

    # jar = requests.cookies.RequestsCookieJar()
    # for navcookie in driver.get_cookies():
        # jar.set(navcookie.get('name'), navcookie.get('value'), domain=navcookie.get('domain'), path=navcookie.get('path'))
    
    # WARN: No se estan pasando las cookies del navegador a get_login_new_cookie
    new_cookies, view_state = get_login_new_cookie(user_agent=ua)
    if not new_cookies:
        return False

    # Estableciendo las nuevas cookies
    for cookie in new_cookies:
        print('[INFO] - Estableciendo cookie: {}'.format(cookie.name))
        driver.delete_cookie(cookie.name)
        cdict = {
            'name': cookie.name, 'value': cookie.value, 
            'path': cookie.path, 'domain': cookie.domain, 
            'secure': cookie.secure, 'expiry': cookie.expires,
        }
        driver.add_cookie(cdict)
    
    # Estableciendo el nuevo ViewState
    if not driver.find_elements_by_name('javax.faces.ViewState'):
        print('[ERROR] - No se encontraron elementos del ViewState')
        return False
    
    driver.execute_script("""\
    document.querySelectorAll('input[name="javax.faces.ViewState"]').forEach((e, i) => { e.value="%s" })
    """ % view_state)
    
    time.sleep(0.5)
    
    return True
