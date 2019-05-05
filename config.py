# -*- coding: utf-8 -*-
import os
import collections

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import main


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

# Acciones
# CERTIFICADOS, LEGALIZACIONES Y VISADOS
ACTIONS_LIST = [
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectPais_label',
        'tag_name': 'label',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            # ('<!-check-procesing-modal-!>', []),
            ('send_keys', ['CUBA']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectTipoDocumento_label',
        'tag_name': 'label',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('send_keys', ['CERTIFICADOS, LEGALIZACIONES Y VISADOS']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:selectNoLegalizados_label',
        'tag_name': 'label',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('send_keys', ['1']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:doc:0:noMinrex',
        'tag_name': 'label',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('send_keys', ['213']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:nombre',
        'tag_name': 'input',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('send_keys', ['JOSE']), # Enviamos los datos de la columna pais (<!-data-!>)
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:ApellidoPat',
        'tag_name': 'input',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('send_keys', ['CASTILLO']), # Enviamos los datos de la columna pais (<!-data-!>)
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:ApellidoMat',
        'tag_name': 'input',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('send_keys', ['LORENZO']), # Enviamos los datos de la columna pais (<!-data-!>)
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:fechaNacimiento_input',
        'tag_name': 'input',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('send_keys', ['15/06/1985']), # Enviamos los datos de la columna pais (<!-data-!>)
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:sexo_label',
        'tag_name': 'label',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('pause', [0.8]), # Pause de 0.5 segundos
            ('send_keys', ['HOMBRE']), # Enviamos los datos de la columna pais (<!-data-!>)
            ('send_keys', [Keys.ENTER]), # Damos enter
        ]
    },
    {
        'action_type': 'navigator', # Especifica que tipo de accion es
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:telmovil',
        'tag_name': 'input',
        'data': (None, None), # Especifica el origen de los datos que se utilizaran para llenar el campo
        'fill_method': 'actions_chain',
        'actions_chain': [
            ('click', ['<!-element-!>']),  # Damos un click en el elemento
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('<!-check-procesing-modal-!>', []),
            ('pause', [0.5]), # Pause de 0.5 segundos
            ('send_keys', ['58692356']), # Enviamos los datos de la columna pais (<!-data-!>)
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
    },
    # Accion para Captcha de Google
    {
        'action_type': 'function', # Especifica que tipo de accion es
        'function': main.action_ask_completation_captcha,    # Nombre de la funcion que se ejeuctara en este paso
    },
    # Accion para testear que el calendario este visible
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:schedule',
        'tag_name': 'div',
        'data': (None, None),
        'fill_method': 'actions_chain',
        'actions_chain': [],
    },
    # Accion para trabajo en el Calendario
    {
        'action_type': 'function', # Especifica que tipo de accion es
        'function': main.procesar_calendario,    # Nombre de la funcion que se ejeuctara en este paso
    },
]
"""
# Visas
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
            ('pause', [0.5]), # Pause de 0.5 segundos
            # ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('pause', [0.2]),
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
            ('pause', [0.5]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('pause', [0.2]),
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
            ('pause', [0.5]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('pause', [0.2]),
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
            ('pause', [1]),
            ('<!-check-procesing-modal-!>', []),    # Magic para testear modal "Procesando..."
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
            ('pause', [0.5]),
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
    },
    # Accion para Captcha de Google
    {
        'action_type': 'function', # Especifica que tipo de accion es
        'function': main.action_ask_completation_captcha,    # Nombre de la funcion que se ejeuctara en este paso
    },
    # Accion para testear que el calendario este visible
    {
        'action_type': 'navigator',
        'find_by': By.ID,
        'selector': 'formRegistroCitaExtranjero:schedule',
        'tag_name': 'div',
        'data': (None, None),
        'fill_method': 'actions_chain',
        'actions_chain': [],
    },
    # Accion para trabajo en el Calendario
    {
        'action_type': 'function', # Especifica que tipo de accion es
        'function': main.procesar_calendario,    # Nombre de la funcion que se ejeuctara en este paso
    },
]
"""
