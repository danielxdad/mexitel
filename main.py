# -*- coding: utf-8 -*-
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
    MoveTargetOutOfBoundsException, JavascriptException, StaleElementReferenceException

import config
import cal


driver = None   # Variable global para WebDriver handler
args = None     # Variable global para parametros de la linea de comandos


# From: http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
def wait_for(condition_function, timeout=30):
    start_time = time.time()
    while time.time() < start_time + timeout:
        if condition_function():
            return True
        else:
            time.sleep(1)
    raise TimeoutException()


class wait_for_page_load(object):
    def __init__(self, browser, timeout=60):
        self.browser = browser
        self.timeout = timeout

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        ready_state = self.browser.execute_script('return window.document.readyState;')
        return new_page.id != self.old_page.id and ready_state == 'complete'

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


def init_driver_instance(implicitly_wait=4):
    """
    Inicia el manejador de Firefox
    :param implicitly_wait: Tiempo de espera para carga y busqueda de elementos en las paginas.
    :return: Instancia de webdriver
    """
    global args

    fp = webdriver.FirefoxProfile()
    # Lenguage por defecto
    fp.set_preference("intl.accept_languages", 'es-ES, es, en-US, en')
    # No bloqueamos el contenido mixto (https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content)
    fp.set_preference("security.mixed_content.block_active_content", False)
    fp.set_preference("network.http.max-persistent-connections-per-server", 4)
    fp.set_preference("network.tcp.keepalive.idle_time", 7200)
    fp.set_preference('devtools.console.stdout.content', True)
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
    with wait_for_page_load(driver):
        try:
            element = driver.find_element(By.ID, 'btnLoginII')
        except NoSuchElementException:
            print('[ERROR] - No se puede encontrar el elemento "btnLoginII" en la pagina de login')
            return False
        else:
            try:
                element.click()
            except TimeoutException:
                return False
    
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
            time.sleep(0.7)


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


def execute_action_navigator(driver, action, row):
    """
    Ejecuta una accion en el navegador
    :param driver: Instancia de WebDriver
    :param action: Diccionario que describe la accion a ejecutar
    :param row: Registro(row) del DataFrame con informacion de cliente
    :return: Boolean True o False
    """
    # Hacemos un scroll al elemento para mostrarlo en el ViewPort
    try:
        driver.execute_script('window.document.getElementById("{}").scrollIntoView(false)'.format(action['selector']))
    except JavascriptException as error:
        print('[ERROR] - JS exception en mail.execute_action_navigator: {} - {}'.format(error, action['selector']))
        return False
    
    time.sleep(0.1)

    data_source, data_field = action['data']
    if data_source == 'dataframe' and data_field not in row:
        print('[ERROR] - La columna "{}" no existe en el DataFrame.'.format(data_field))
        return False
    
    # Realizamos las acciones de establecimiento de valor
    if action['fill_method'] == 'actions_chain' and len(action['actions_chain']):
        action_chain = ActionChains(driver)
        for ac in action['actions_chain']:
            # Obtenemos el elemento por el metodo especificado en la configuracion
            try:
                element = driver.find_element(action['find_by'], action['selector'])
            except NoSuchElementException:
                print('[ERROR] - No se puede encontrar el elemento "{}"'.format(action['selector']))
                return False

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
        
        # Obtenemos el elemento por el metodo especificado en la configuracion
        try:
            element = driver.find_element(action['find_by'], action['selector'])
        except NoSuchElementException:
            print('[ERROR] - No se puede encontrar el elemento "{}"'.format(action['selector']))
            return False

        try:
            eval('action_chain.perform()', None, {'action_chain': action_chain, 'element': element})
        except MoveTargetOutOfBoundsException:
            print('[ERROR] - El elemento "{}" esta fuera del ViewPort.'.format(action['selector']))
            return False
        except StaleElementReferenceException as err:
            print('[ERROR] - Error de referencia expirada: {}.'.format(err))
        else:
            # Esperamos porque el modal de "Procesando..." se oculte, este se muestra al realizar una accion
            check_procesing_modal(driver)
    
    return True


def action_ask_completation_captcha(driver=None, *args, **kwargs):
    """
    Funcion que pregunta en la consola si se ha completado el captcha de Google. Se invocara desde la lista de acciones.
    :param driver: Instancia de driver de navegador
    :param args: Argumentos pasado en la linea de comandos
    :return: Boolean
    """
    for iframe in driver.find_elements_by_tag_name('iframe'):
        driver.switch_to.frame(iframe)
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true });")
        except JavascriptException as err:
            print('[ERROR] - JSException main.action_ask_completation_captcha: {}'.format(err))
        
        driver.switch_to.default_content()

    return input('[QUEST] - ¿Haz completado el Captcha de Google? (si/no): ').lower() in ['si', 's']


def procesar_calendario(driver=None, *args, **kwargs):
    """
    Funcion que invoca el procesamiento del calendario
    :param driver: Instancia de driver de navegador
    :param args: Argumentos pasado en la linea de comandos
    :return: Boolean
    """
    mes = kwargs.get('mes')
    anio = kwargs.get('anio')
    action_list = kwargs.get('action_list')
    row = kwargs.get('row')
    return cal.calendar(driver, mes, anio, action_list, row)


def parse_argument():
    """
    Parsea los parametros de la linea de comandos
    """
    parser = argparse.ArgumentParser(description='Mexitel fucker ;)')
    parser.add_argument('--mes', nargs=1, type=str, choices=cal.MESES, help='Mes del calendario.')
    parser.add_argument('--anio', nargs=1, type=int, choices=cal.ANIOS, help='Anio del calendario.')
    parser.add_argument('--visas', action='store_true', help='Utilizar lista de acciones para Visas.')
    parser.add_argument('--tor', action='store_true', help='Pasar por proxy local TOR SOCKSv5.')
    parser.add_argument('file', nargs=1, help='Fichero con datos de clientes.')
    return parser.parse_args()


def main():
    """
    Funcion inicial de la app
    """
    global driver, args
    args = parse_argument()

    excel_file = pathlib.Path(args.file[0])
    if not excel_file.exists():
        print('[ERROR] - El fichero especificado no existe.')
        return -1

    # Leemos el fichero Excel(XLS) con datos de clientes
    df = pd.read_excel(
        excel_file,
        converters={
            'fecha_nacimiento': lambda val: str(val),
            'telefono_movil': lambda val: str(val),
        }
    )

    if args.visas:
        print('[INFO] - Utilizando cadena de acciones de "VISAS".')
    else:
        print('[INFO] - Utilizando cadena de acciones de "CERTIFICADOS, LEGALIZACIONES Y VISADOS".')
    
    driver = init_driver_instance()

    # Accedemos a la pagina de login
    while login(driver) is False:
        time.sleep(10)

    # Test relogin
    """
    with wait_for_page_load(driver):
        driver.get('https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',)
    time.sleep(1.5)
    utils.relogin(driver)
    with wait_for_page_load(driver):
        driver.get('https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',)
    time.sleep(5)
    input('>>')
    return 
    """

    for index, row in df.iterrows():
        if row['procesado'].lower() != 'no':
            continue

        # Testeamos la url actual y el titulo de la pagina
        if not test_url_page_title(
            driver,
            'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
            'Citas SRE'
        ):
            while login(driver) is False:
                time.sleep(10)
            
        
        # TODO: Sobre escritura de funcion originalHandler para imprimir a consola todas las peticiones/respuestas
        # hechas por el navegador

        # Redefinimos la propiedad navigator.webdriver a false para Captcha de Google
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true });")
        except JavascriptException as error:
            print(error)
            continue

        # Boton "Cerrar sesion", hacemos que si se da click o se invoca desde JS no haga nada
        try:
            driver.execute_script('document.getElementById("headerForm:nonAjax").onclick=function(){return true}')
        except JavascriptException as error:
            print(error)
            continue

        # Sobreescritura de funcion "handleAjaxComplete"
        driver.execute_script("""\
            window.handleAjaxComplete = (xml, xhr, status, updateHandler) => {
                session = xml.getElementsByTagName('session-expired');
                if (session.length > 0){
                    if(session[0].childNodes[0].nodeValue =='true'){
                        // PF('sessionStatus').show();
                    }
                }else{
                    window.clearTimeout(sessionTimer);
                    sessionTimer=window.setTimeout(function(){mostrarModalExpira()},sessionTimeoutSecs*800);
                    window.clearTimeout(ajaxTimer);
                    originalHandle(xml, status, xhr, updateHandler);
                }
            };
            console.log('handleAjaxComplete reescrita')
            //console.log(handleAjaxComplete.toSource())
        """)

        print('[INFO] - Procesando registro {} - {} {}...'.format(index + 1, row['nombre'], row['apellidos']))

        action_list = config.ACTIONS_LIST_VISAS if args.visas else config.ACTIONS_LIST_CERT_LEG_VIS
        for action_index, action in enumerate(action_list):
            if action['action_type'] == 'navigator':
                if not execute_action_navigator(driver, action, row):
                    return -1

            elif action['action_type'] == 'function':
                if 'function' not in action:
                    print('[ERROR] - La clave "function" no existe en la accion "function", indice: %d' % action_index)
                    return -1 
                
                func = action['function']
                if not callable(func):
                    print('[ERROR] - El valor de la clave "function" en accion "function" no se una funcion, indice: %d' % action_index)
                    return -1

                if not func(driver, mes=args.mes[0], anio=args.anio[0], action_list=action_list, row=row):
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
