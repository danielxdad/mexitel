# -*- coding: utf-8 -*-
import sys
import argparse
import time
import os
import pathlib
import atexit
from urllib import parse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    MoveTargetOutOfBoundsException

import config
import cal
from cal import MESES, ANIOS, calendar

driver = None   # Variable global para WebDriver handler
args = None     # Variable global para parametros de la linea de comandos


# From: http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
def wait_for(condition_function, timeout=30):
    start_time = time.time()
    while time.time() < start_time + timeout:
        if condition_function():
            return True
        else:
            time.sleep(0.5)
    raise TimeoutException()


class wait_for_page_load(object):
    def __init__(self, browser, timeout=60):
        self.browser = browser
        self.timeout = timeout

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded, self.timeout)


def test_url_page_title(driver, url, title):
    """
    Testea que la URL en driver.current_url sea igual a "url" y driver.title sea igual a "title".
    @param driver: Instancia de driver de navegador
    @param url: URL a testear
    @param title: Titulo a testear
    @return bool: Devuelve True o False como resultado de coincidencia
    """
    parser_driver_url = parse.urlparse(driver.current_url)
    parser_url = parse.urlparse(url)
    pdu_tuple = (parser_driver_url.scheme, parser_driver_url.netloc, parser_driver_url.path)
    pu_tuple = (parser_url.scheme, parser_url.netloc, parser_url.path)
    return pdu_tuple == pu_tuple and driver.title.lower() == title.lower()


def init_driver_instance(webdriver_type='firefox', implicitly_wait=4):
    """
    Inicia el manejador de Chrome
    @param implicitly_wait: Tiempo de espera para carga y busqueda de elementos en las paginas.
    @return: Instancia de selenium.webdriver.Chrome
    """
    global args

    if webdriver_type == 'firefox':
        fp = webdriver.FirefoxProfile()
        # Lenguage por defecto
        fp.set_preference("intl.accept_languages", 'es-ES, es, en-US, en')
        # No bloqueamos el contenido mixto (https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content)
        fp.set_preference("security.mixed_content.block_active_content", False)
        # Si se ha especificado el parametro --tor en la linea de comandos
        if args.tor:
            # Establecemos el Proxy SOCKSv5 en el navegador
            fp.set_preference("network.proxy.type", 1)
            fp.set_preference("network.proxy.socks", "127.0.0.1")
            fp.set_preference("network.proxy.socks_port", 9050)
            fp.set_preference("network.proxy.socks_version", 5)
        fp.update_preferences()
        driver = webdriver.Firefox(firefox_profile=fp)
        driver.install_addon(os.path.join(config.BASE_DIR, 'disconnect-5.18.27-fx.xpi'), True)
    elif webdriver_type == 'chrome':
        driver = webdriver.Chrome(config.CHROME_DRIVER_PATH)
    else:
        raise RuntimeError('El tipo de webdriver especificado no esta soportado: {}'.format(webdriver_type))

    driver.implicitly_wait(implicitly_wait)
    driver.maximize_window()

    return driver


def nav_to_page(driver, url):
    """
    Navega a una URL especificada
    @param driver: Driver de navegador
    @param url: URL a navegar
    @return bool: Devuelve True o False
    """
    parser = parse.urlparse(url)
    if parser.scheme not in ['http', 'https']:
        raise ValueError('El protocolo de la URL es incorrecto: {}'.format(repr(parser.scheme)))
    
    if not parser.netloc:
        raise ValueError('No se ha especificado un dominio en la URL: {}'.format(repr(url)))

    with wait_for_page_load(driver):
        # driver.get('https://www.google.com/search?%s' % urllib.urlencode({'q': keyword.keyword}))
        driver.get(url)


def login(driver):
    """
    Funcion para logearse en la pagina
    :param driver: Instancia de driver de navegador
    :return bool: Devuelve True o False
    """
    try:
        nav_to_page(driver, config.LOGIN_URL)
    except ValueError as err:
        print('[ERROR] - {}'.format(err))
        return False
    except TimeoutException:
        print('[ERROR] - Tiempo de espera agotado al acceder a "{}"'.format(config.LOGIN_URL))
        return False
    except WebDriverException as error:
        print('[ERROR] - Error al acceder a "{}": {}'.format(config.LOGIN_URL, error.msg))
        return False
    
    # Username input element
    try:
        element = driver.find_element(By.ID, config.LOGIN_FIELD_USERNAME_ID)
    except NoSuchElementException:
        print('[ERROR] - No se puede encontrar el elemento "{}" en la pagina de login'.format(config.LOGIN_FIELD_USERNAME_ID))
        return False
    else:
        element.clear()
        element.send_keys(config.USERNAME)
    
    # Password input element
    try:
        element = driver.find_element(By.ID, config.LOGIN_FIELD_PASSWORD_ID)
    except NoSuchElementException:
        print('[ERROR] - No se puede encontrar el elemento "{}" en la pagina de login'.format(config.LOGIN_FIELD_PASSWORD_ID))
        return False
    else:
        element.clear()
        element.send_keys(config.PASSWORD)
    
    # Boton "Ingresar"
    try:
        element = driver.find_element(By.ID, 'btnLoginII')
    except NoSuchElementException:
        print('[ERROR] - No se puede encontrar el elemento "btnLoginII" en la pagina de login')
        return False
    else:
        element.click()
    
    return True


def check_procesing_modal(driver):
    """
    Testea que el modal "Procesando..." este visible y espera a su cierre.
    :param driver: Instancia de WebDriver
    return None
    """
    # Esperamos porque el modal de "Procesando..." se oculte, este se muestra al realizar una accion
    try:
        element = driver.find_element_by_id('j_idt24')
    except NoSuchElementException:
        pass
    else:
        while element.is_displayed():
            time.sleep(0.5)


def exithandler():
    """
    Exit handler para cerrar webdriver
    :return: None
    """
    global driver
    if isinstance(driver, webdriver.Firefox) or isinstance(driver, webdriver.Chrome):
        try:
            driver.close()
        except:
            pass


def action_ask_completation_captcha(driver=None, args=None):
    """
    Funcion que pregunta en la consola si se ha completado el captcha de Google. Se invocara desde la lista de acciones.
    :param driver: Instancia de driver de navegador
    :param args: Argumentos pasado en la linea de comandos
    :return: Boolean
    """
    return input('[QUEST] - ¿Haz completado el Captcha de Google? (si/no): ').lower() in ['si', 's']


def execute_action_navigator(action, row):
    """
    Ejecuta una accion en el navegador
    :param action: Diccionario que describe la accion a ejecutar
    :param row: Registro(row) del DataFrame con informacion de cliente
    :return: Boolean True o False
    """
    # Hacemos un scroll al elemento para mostrarlo en el ViewPort
    driver.execute_script('document.getElementById("{}").scrollIntoView(false)'.format(action['selector']))
    time.sleep(0.1)

    # Obtenemos el elemento por el metodo especificado en la configuracion
    try:
        element = driver.find_element(action['find_by'], action['selector'])
    except NoSuchElementException:
        print('[ERROR] - No se puede encontrar el elemento "{}"'.format(action['selector']))
        return False

    data_source, data_field = action['data']
    if data_source == 'dataframe' and data_field not in row:
        print('[ERROR] - La columna "{}" no existe en el DataFrame.'.format(data_field))
        return False
    
    # Realizamos las acciones de establecimiento de valor
    if action['fill_method'] == 'actions_chain' and len(action['actions_chain']):
        action_chain = ActionChains(driver)
        for ac in action['actions_chain']:
            params = []
            for p in ac[1]:
                if p == '<!-data-!>':
                    if data_source == 'dataframe':
                        params.append(row[data_field])
                elif p == '<!-element-!>':
                    params.append(element)
                else:
                    params.append(p)
            
            # Hay que emular la escritura de una persona con un tiempo de espera entre cada pulsacion
            if ac[0] == 'send_keys':
                if action['tag_name'] == 'label':
                    for key in params[0]:
                        if type(key) == str:
                            code = 'action_chain.{}("{}")'.format(ac[0], key)
                        else:
                            code = 'action_chain.{}({})'.format(ac[0], key)
                        eval(code, None, {'action_chain': action_chain, 'params': params, 'element': element})
                        eval('action_chain.pause(0.07)')
                
                else:   # Si es un campo "INPUT" no hacemos el tiempo de espera entre cada pulsacion
                    action_chain.send_keys(params[0])
            
            # Chequemos la presencia del modal "Procesando..."
            elif ac[0] == '<!-check-procesing-modal-!>':
                check_procesing_modal(driver)
            
            else:
                eval('action_chain.{}(*params)'.format(ac[0]), None, 
                    {'action_chain': action_chain, 'params': params, 'element': element})
        
        try:
            eval('action_chain.perform()', None, {'action_chain': action_chain, 'element': element})
        except MoveTargetOutOfBoundsException:
            print('[ERROR] - El elemento "{}" esta fuera del ViewPort.'.format(action['selector']))
            return False
        else:
            # Esperamos porque el modal de "Procesando..." se oculte, este se muestra al realizar una accion
            check_procesing_modal(driver)
    
    return True


def procesar_calendario(driver=None, args=None):
    """
    Funcion que invoca el procesamiento del calendario
    :param driver: Instancia de driver de navegador
    :param args: Argumentos pasado en la linea de comandos
    :return: Boolean
    """
    return cal.calendar(driver, args.mes[0], args.anio[0])


def main():
    """
    Funcion inicial de la app
    """
    global driver, args
    parser = argparse.ArgumentParser(description='Mexitel fucker ;)')
    parser.add_argument('--mes', nargs=1, type=str, choices=cal.MESES, help='Mes del calendario')
    parser.add_argument('--anio', nargs=1, type=int, choices=cal.ANIOS, help='Anio del calendario')
    parser.add_argument('--tor', action='store_true', help='Pasar por proxy local TOR SOCKSv5')
    parser.add_argument('file', nargs=1, help='Fichero con datos de clientes')
    args = parser.parse_args()

    excel_file = pathlib.Path(args.file[0])
    if not excel_file.exists():
        print('[ERROR] - El fichero especificado no existe.')
        return -1

    # Leemos el fichero Excel(XLS) con datos de clientes
    df = pd.read_excel(
        excel_file,
        converters={
            # 'procesado': lambda val: False if val.lower() == 'no' else True,
            'fecha_nacimiento': lambda val: str(val),
            'telefono_movil': lambda val: str(val),
        }
    )

    driver = init_driver_instance()

    # Accedemos a la pagina de login
    with wait_for_page_load(driver):
        if login(driver) is False:
            # Si no nos pudimos logear salimos de la app
            return -1
    
    for index, row in df.iterrows():
        if row['procesado'].lower() != 'no':
            continue

        while driver.execute_script('return window.document.readyState;') != 'complete':
            time.sleep(1)
        
        # Testeamos la url actual y el titulo de la pagina
        if not test_url_page_title(driver, 
            'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
            'Citas SRE'):
            print('[ERROR] - No se pudo acceder a la pagina de citas.')
            return -1

        # Boton "Cerrar sesion", hacemos que si se da click o se invoca desde JS no haga nada
        driver.execute_script('document.getElementById("headerForm:nonAjax").onclick=function(){return true}')

        print('[INFO] - Procesando registro {} - {} {}...'.format(index + 1, row['nombre'], row['apellidos']))
        for action_index, action in enumerate(config.ACTIONS_LIST):
            if action['action_type'] == 'navigator':
                if not execute_action_navigator(action, row):
                    return -1

            elif action['action_type'] == 'function':
                if 'function' not in action:
                    print('[ERROR] - La clave "function" no existe en la accion "function", indice: %d' % action_index)
                    return -1 
                
                func = action['function']
                if not callable(func):
                    print('[ERROR] - El valor de la clave "function" en accion "function" no se una funcion, indice: %d' % action_index)
                    return -1

                if not func(driver, args):
                    print('[ERROR] - La funcion de accion "function" a devuelto un valor False, indice: %d' % action_index)
                    return -1

            else:
                print('[ERROR] - Un tipo de accion no es soportada "{} - {}"'.format(action_index + 1, action['action_type']))
                return -1

        while True:
            try:
                val = input('[INFO] - El registro {} - "{} {}" ha sido procesado? (si/no):'.format(
                    index + 1, row['nombre'], row['apellidos'])).lower()
            except EOFError:
                continue
            else:
                if val == 'si':
                    df.loc[index, 'procesado'] = 'SI'
                break

        try:
            url = 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/' \
                'registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true'
            nav_to_page(driver, url)
        except ValueError as err:
            print('[ERROR] - {}'.format(err))
            return False
        except TimeoutException:
            print('[ERROR] - Tiempo de espera agotado al acceder a "{}"'.format(url))
            return False
        except WebDriverException as error:
            print('[ERROR] - Error al acceder a "{}": {}'.format(url, error.msg))
            return False
    
    # Actualizamos los registros en el fichero Excel que hayan sido procesados correctamente
    with pd.ExcelWriter(str(excel_file.resolve())) as writer:
        df.to_excel(writer, index=False)
    
    try:
        input('[INFO] - Presione "Enter" para salir...')
    except EOFError:
        pass

    return 0

if __name__ == "__main__":
    atexit.register(exithandler)
    try:
        exit(main())
    except KeyboardInterrupt:
        print('')
        exit(0)
