# -*- coding: utf-8 -*-
import os
import collections

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGIN_URL = 'https://mexitel.sre.gob.mx/citas.webportal/pages/public/login/login.jsf'
USERNAME = 'danielxdad@gmail.com'
PASSWORD = 'Xdad88121700264/*-'
LOGIN_FIELD_USERNAME_ID = 'j_username'
LOGIN_FIELD_PASSWORD_ID = 'j_password'

CHROME_DRIVER_PATH = os.path.join(BASE_DIR, 'chromedriver')
if not os.path.exists(CHROME_DRIVER_PATH):
    print('ChromeDriver no existe en el path "{}"'.format(CHROME_DRIVER_PATH))
    exit()

FIREFOX_PROFILE_PATH = os.path.join(BASE_DIR, 'firefox_profile/')

PDF_TMP_IMAGES_DIR = os.path.join(BASE_DIR, 'pdf/images/')

MAP_COLUMNS_INPUT = collections.OrderedDict([
    ('pais', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPais_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            # El primer elemento de cada tupla es un metodo de "selenium.webdriver.action_chains.ActionChains", 
            # el segundo (lista) son los parametros
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.4]), # Pause de 0.5 segundos
            ('send_keys', ['<!-data-!>']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    }),
    ('documento', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTipoDocumento_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('tramite', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTramite_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('detalle', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTipoTramite_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('pasaporte', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:noPasapAnt',
        'tag_name': 'input',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
        ]
    }),
    ('pais_emision_pasaporte', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPaisPasaporte_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('nombre', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:nombre',
        'tag_name': 'input',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
        ]
    }),
    ('apellidos', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:Apellidos',
        'tag_name': 'input',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.7]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('pause', [0.5]),
            ('send_keys', ['<!-data-!>']),
        ]
    }),
    ('nacionalidad', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectNacionalidad_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('fecha_nacimiento', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:fechaNacimiento_input',
        'tag_name': 'input',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
        ]
    }),
    ('pais_nacimiento', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPaisNacimiento_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('sexo', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:sexo_label',
        'tag_name': 'label',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    }),
    ('telefono_movil', {
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:telmovil',
        'tag_name': 'input',
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('send_keys', ['<!-data-!>']),
        ]
    }),
])
