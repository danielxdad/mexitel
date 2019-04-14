# -*- coding: utf-8 -*-
import sys
import argparse
import time
import os
import pathlib
from urllib import parse

import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    MoveTargetOutOfBoundsException

import config


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
    if driver.current_url == url and driver.title == title:
        return True
    return False


def init_driver_instance(webdriver_type='firefox', implicitly_wait=2):
    """
    Inicia el manejador de Chrome
    @param implicitly_wait: Tiempo de espera para carga y busqueda de elementos en las paginas.
    @return: Instancia de selenium.webdriver.Chrome
    """
    if webdriver_type == 'firefox':
        if not os.path.exists(config.FIREFOX_PROFILE_PATH):
            os.makedirs(config.FIREFOX_PROFILE_PATH)
        fp = webdriver.FirefoxProfile(config.FIREFOX_PROFILE_PATH)
        driver = webdriver.Firefox(firefox_profile=fp)
    elif webdriver_type == 'chrome':
        driver = webdriver.Chrome(config.CHROME_DRIVER_PATH)
    else:
        raise RuntimeError('El tipo de webdriver especificado no esta soportado: {}'.format(webdriver_type))

    driver.implicitly_wait(implicitly_wait)
    driver.maximize_window()
    # driver.minimize_window()
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
    @param driver: Instancia de driver de navegador
    @return bool: Devuelve True o False
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


def check_procesing_modal(driver):
    """
    Testea que el modal "Procesando..." este visible y espera a su cierre.
    @param driver: Instancia de WebDriver
    return None
    """
    # Esperamos porque el modal de "Procesando..." se oculte, este se muestra al realizar una accion
    element = None
    time.sleep(0.7)
    for _ in range(20):
        try:
            element = driver.find_element(By.ID, 'j_idt24')
        except NoSuchElementException:
            break
        else:
            break
        time.sleep(0.2)

    if element:
        while element.is_displayed():
            time.sleep(0.3)

def main():
    """
    Funcion inicial de la app
    """
    parser = argparse.ArgumentParser(description='Mexitel fucker ;)')
    parser.add_argument('file', nargs=1, help='fichero con datos de pasaporte')
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
    login(driver)
    while driver.execute_script('return window.document.readyState;') != 'complete':
        time.sleep(0.5)

    for index, row in df.iterrows():
        if row['procesado'].lower() != 'no':
            continue

        # Testeamos la url actual y el titulo de la pagina
        if not test_url_page_title(driver, 
            'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'Citas SRE'):
            print('[ERROR] - No se pudo acceder a la pagina de citas.')
            return

        print('[INFO] - Procesando registro {} - {} {}...'.format(index + 1, row['nombre'], row['apellidos']))
        for column in config.MAP_COLUMNS_INPUT:
            mci = config.MAP_COLUMNS_INPUT[column]

            if column not in row:
                print('[ERROR] - La columna "{}" no existe en el DataFrame.'.format(column))
                return -1

            # Obtenemos el elemento por el metodo especificado en la configuracion
            try:
                element = driver.find_element(mci['find_by'], mci['selector'])
            except NoSuchElementException:
                print('[ERROR] - No se puede encontrar el elemento "{}" asociado a la columna "{}"'.format(mci['selector'], 
                    column))
                return -1
            
            # Hacmos un scroll al elemento para mostrarlo en el ViewPort
            driver.execute_script('document.getElementById("{}").scrollIntoView(false)'.format(mci['selector']))
            time.sleep(0.5)
            
            # Realizamos las acciones de establecimiento de valor
            if mci['fill_method'] == 'actions_chain':
                action_chain = ActionChains(driver)
                for ac in mci['actions_chain']:
                    params = []
                    for p in ac[1]:
                        if p == '<!-data-!>':
                            params.append(row[column])
                        elif p == '<!-element-!>':
                            params.append(element)
                        else:
                            params.append(p)
                    
                    # Hay que emular la escritura de una persona con un tiempo de espera entre cada pulsacion
                    if ac[0] == 'send_keys':
                        for key in params[0]:
                            if type(key) == str:
                                code = 'action_chain.{}("{}")'.format(ac[0], key)
                            else:
                                code = 'action_chain.{}({})'.format(ac[0], key)
                            eval(code, None, {'action_chain': action_chain, 'params': params, 'element': element})
                            eval('action_chain.pause(0.07)')
                    elif ac[0] == '<!-check-procesing-modal-!>':
                        check_procesing_modal(driver)
                    else:
                        eval('action_chain.{}(*params)'.format(ac[0]), None, 
                            {'action_chain': action_chain, 'params': params, 'element': element})
                
                try:
                    eval('action_chain.perform()', None, {'action_chain': action_chain, 'element': element})
                except MoveTargetOutOfBoundsException:
                    print('[ERROR] - El elemento "{}" esta fuera del ViewPort.'.format(mci['selector']))
                    return -1
                else:
                    # Esperamos porque el modal de "Procesando..." se oculte, este se muestra al realizar una accion
                    check_procesing_modal(driver)

            else:
                print('[ERROR] - El metodo de llenado para la columna "{}" es invalido.'.format(column))
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
        input('[INFO] - Presione una tecla para salir')
    except EOFError:
        pass

    driver.close()
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        exit(0)
