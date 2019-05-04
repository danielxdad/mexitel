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

PDF_TMP_DIR = os.path.join(BASE_DIR, 'pdf/')
PDF_TMP_IMAGES_DIR = os.path.join(BASE_DIR, 'pdf/images/')

# Email account config
EMAIL_HOST = 'imap.gmail.com'
EMAIL_ACCOUNT = 'danielxdad@gmail.com'
EMAIL_PASSWORD = 'xdad641489542976'

# Fichero para registro de UIDs de email obtenidos desde servidor IMAP para evitar doble procesamiento.
FILE_EMAIL_UID_REG = os.path.join(BASE_DIR, 'email_uid_register.txt')
if not os.path.exists(FILE_EMAIL_UID_REG):
    with open(FILE_EMAIL_UID_REG, 'w') as fd:
        pass

# Accciones
ACTIONS_LIST = [
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPais_label',
        'tag_name': 'label',
        'data': ('dataframe', 'pais'), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            # El primer elemento de cada tupla es un metodo de "selenium.webdriver.action_chains.ActionChains", 
            # el segundo (lista) son los parametros
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.4]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTipoDocumento_label',
        'tag_name': 'label',
        'data': ('dataframe', 'documento'), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTramite_label',
        'tag_name': 'label',
        'data': ('dataframe', 'tramite'), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTipoTramite_label',
        'tag_name': 'label',
        'data': ('dataframe', 'detalle'), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:noPasapAnt',
        'tag_name': 'input',
        'data': ('dataframe', 'pasaporte'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPaisPasaporte_label',
        'tag_name': 'label',
        'data': ('dataframe', 'pais_emision_pasaporte'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:nombre',
        'tag_name': 'input',
        'data': ('dataframe', 'nombre'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:Apellidos',
        'tag_name': 'input',
        'data': ('dataframe', 'apellidos'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [1.5]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('pause', [0.7]),
            ('send_keys', ['<!-data-!>']),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectNacionalidad_label',
        'tag_name': 'label',
        'data': ('dataframe', 'nacionalidad'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:fechaNacimiento_input',
        'tag_name': 'input',
        'data': ('dataframe', 'fecha_nacimiento'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPaisNacimiento_label',
        'tag_name': 'label',
        'data': ('dataframe', 'pais_nacimiento'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:sexo_label',
        'tag_name': 'label',
        'data': ('dataframe', 'sexo'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
            ('send_keys', [Keys.ENTER]),
        ]
    },
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:telmovil',
        'tag_name': 'input',
        'data': ('dataframe', 'telefono_movil'),
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),
            ('pause', [0.4]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('send_keys', ['<!-data-!>']),
        ]
    },
    # Hacer scroll al boton "Buscar citas"
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:buscarCita',
        'tag_name': 'button',
        'data': (None, None),
        'fill_method': 'actions_chain',
        'actions_chain': []
    }
]
