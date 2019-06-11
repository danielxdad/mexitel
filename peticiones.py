# -*- coding: utf-8 -*-
from lxml import etree
import requests
from colorama import Fore

import utils


def validate_response_button_buscar_citas(response: requests.Response) -> bool:
    """
    Funcion invocada desde accion "Boton Buscar citas" para validar el captcha de google si esta bien
    :param response: Instancia de requests.Response
    :return: Boolean
    """
    if response.headers['content-type'].find('text/xml') == -1:
        return False

    parser = etree.XMLParser(load_dtd=False, no_network=True, ns_clean=True, remove_comments=True)
    try:
        root = etree.fromstring(response.content, parser)
    except etree.ParseError as error:
        utils.print_message('[ERROR] - Parseando respuesta XML en peticiones.validate_response_button_buscar_citas: "{}"'.format(error),
                            color=Fore.RED)
        return False
    else:
        el = root.xpath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]')
        if not el:
            return False
        
        if el[0].text.find('El texto introducido en el captcha no coincide') != -1:
            utils.print_message('[ERROR] - El captcha enviado es invalido.', color=Fore.RED)
            return False
    
    return True


def month_calendar_response_parser(response: requests.Response) -> dict:
    """
    Parsea los datos de respuesta de peticion de obtencion de eventos de calendario en modo Mes
    :param response: Instancia de requests.Response
    :return: Diccionario(JSON) con eventos de calendario o None en caso de error
    """
    return utils.parse_calendar_data_month(response.content)


# Peticion para obtecion de eventos de calendario en modo mes
CALENDAR_MONTH_REQUEST = {
    'name': 'Calendario Mes',
    'method': 'POST',
    'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
    'request_headers': {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
        'faces-request': 'partial/ajax',
        'Origin': 'https://mexitel.sre.gob.mx',
        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
        'User-Agent': '',
        'X-Requested-With': 'XMLHttpRequest',
    },
    'form_data': {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.execute': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.render': 'formRegistroCitaExtranjero:schedule',
        'formRegistroCitaExtranjero:schedule': 'formRegistroCitaExtranjero:schedule',
        'formRegistroCitaExtranjero:schedule_start': '',    # 1558821600000, Timestamp de JS en milisegundos
        'formRegistroCitaExtranjero:schedule_end': '',  # 1562450400000, Timestamp de JS en milisegundos
        'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
        'formRegistroCitaExtranjero:schedule_view': 'month',
        'javax.faces.ViewState': '',

    },
    'status_code': 200,
    'response_headers': {
        'content-type': 'text/xml',
    },
    'xml_valid_response': [
        etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:schedule"]'),
        etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
    ],
    'xml_invalid_response': [
        etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
    ],
    'parser_response': month_calendar_response_parser,
}


CALENDAR_MONTH_SELECT_EVENT = {
    'name': 'Calendario Seleccion Evento Mes',
    'method': 'POST',
    'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
    'request_headers': {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
        'faces-request': 'partial/ajax',
        'Origin': 'https://mexitel.sre.gob.mx',
        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
        'User-Agent': '',
        'X-Requested-With': 'XMLHttpRequest',
    },
    'form_data': {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.execute': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.render': 'formRegistroCitaExtranjero reviewForm',
        'javax.faces.behavior.event': 'eventSelect',
        'javax.faces.partial.event': 'eventSelect',
        'formRegistroCitaExtranjero:schedule_selectedEventId': '',
        'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
        'formRegistroCitaExtranjero:selectPais_focus': '',
        'formRegistroCitaExtranjero:selectPais_input': 17,
        # 'formRegistroCitaExtranjero:selectSedeUbicacion_filter': '',
        # 'formRegistroCitaExtranjero:selectTipoDocumento_focus': '',
        # 'formRegistroCitaExtranjero:selectTipoDocumento_input': 3,
        # 'formRegistroCitaExtranjero:selectNoLegalizados_focus': '',
        # 'formRegistroCitaExtranjero:selectNoLegalizados_input': 1,
        # 'formRegistroCitaExtranjero:doc:0:noMinrex': '213',
        'formRegistroCitaExtranjero:teldomicilio': '',
        'formRegistroCitaExtranjero:telmovil': '54265689',
        # g-recaptcha-response:
        'formRegistroCitaExtranjero:schedule_view': 'month',
        'javax.faces.ViewState': '',
    },
    'status_code': 200,
    'response_headers': {
        'content-type': 'text/xml',
    },
    'xml_valid_response': [
        etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
        etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
    ],
    'xml_invalid_response': [
        etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
    ],
}

CALENDAR_GET_DAY_EVENTS = {
    'name': 'Calendario Horas Disponibles',
    'method': 'POST',
    'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
    'request_headers': {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
        'faces-request': 'partial/ajax',
        'Origin': 'https://mexitel.sre.gob.mx',
        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
        'User-Agent': '',
        'X-Requested-With': 'XMLHttpRequest',
    },
    'form_data': {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.execute': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.render': 'formRegistroCitaExtranjero:schedule',
        'formRegistroCitaExtranjero:schedule': 'formRegistroCitaExtranjero:schedule',
        'formRegistroCitaExtranjero:schedule_start': '',    # 1561932000000
        'formRegistroCitaExtranjero:schedule_end': '',  # 1562018400000
        'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
        'formRegistroCitaExtranjero:schedule_view': 'agendaDay',
        'javax.faces.ViewState': '',
    },
    'status_code': 200,
    'response_headers': {
        'content-type': 'text/xml',
    },
    'xml_valid_response': [
        etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:schedule"]'),
        etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
    ],
    'xml_invalid_response': [
        etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
    ],
    'parser_response': month_calendar_response_parser,
}


CALENDAR_SELECT_HOUR_EVENT = {
    'name': 'Calendario Seleccion Hora',
    'method': 'POST',
    'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
    'request_headers': {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
        'faces-request': 'partial/ajax',
        'Origin': 'https://mexitel.sre.gob.mx',
        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
        'User-Agent': '',
        'X-Requested-With': 'XMLHttpRequest',
    },
    'form_data': {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.execute': 'formRegistroCitaExtranjero:schedule',
        'javax.faces.partial.render': 'formRegistroCitaExtranjero reviewForm',
        'javax.faces.behavior.event': 'eventSelect',
        'javax.faces.partial.event': 'eventSelect',
        'formRegistroCitaExtranjero:schedule_selectedEventId': '',  # d70cd62c-3f67-4b8f-8a76-4282bdb42024
        'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
        # formRegistroCitaExtranjero:selectPais_focus:
        # formRegistroCitaExtranjero:selectPais_input: 17
        # formRegistroCitaExtranjero:selectSedeUbicacion_filter:
        # formRegistroCitaExtranjero:selectTipoDocumento_focus:
        # formRegistroCitaExtranjero:selectTipoDocumento_input: 3
        # formRegistroCitaExtranjero:selectNoLegalizados_focus:
        # formRegistroCitaExtranjero:selectNoLegalizados_input: 1
        # formRegistroCitaExtranjero:doc:0:noMinrex: 213
        # formRegistroCitaExtranjero:teldomicilio:
        # formRegistroCitaExtranjero:telmovil: 54265689
        # g-recaptcha-response:
        'formRegistroCitaExtranjero:schedule_view': 'agendaDay',
        'javax.faces.ViewState': '',
    },
    'status_code': 200,
    'response_headers': {
        'content-type': 'text/xml',
    },
    'xml_valid_response': [
        etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
        etree.XPath('/partial-response/changes/update[@id="reviewForm"]'),
        etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
    ],
    'xml_invalid_response': [
        etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
    ],
}

CALENDAR_CONFIRM_CITA = {
    'name': 'Calendario Confirmar Cita',
    'method': 'POST',
    'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
    'request_headers': {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
        'faces-request': 'partial/ajax',
        'Origin': 'https://mexitel.sre.gob.mx',
        'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
        'User-Agent': '',
        'X-Requested-With': 'XMLHttpRequest',
    },
    'form_data': {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': 'reviewForm:confirmarCita',
        'javax.faces.partial.execute': '@all',
        'javax.faces.partial.render': 'formRegistroCitaExtranjero citaForm reviewForm',
        'reviewForm:confirmarCita': 'reviewForm:confirmarCita',
        'reviewForm': 'reviewForm',
        'reviewForm:confirmCodigoSeguridad': '',    # zim235n4
        'reviewForm:confirmToken': '',  # jDD6nVepF3kceQUgRLxrr5Q5P47m2jXd4OgRY9pNh82zgx36CKbBdkSjgV2sSuQY
        'javax.faces.ViewState': '',
    },
    'status_code': 200,
    'response_headers': {
        'content-type': 'text/xml',
    },
    'xml_valid_response': [
        etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
        etree.XPath('/partial-response/changes/update[@id="reviewForm"]'),
        etree.XPath('/partial-response/changes/update[@id="citaForm"]'),
        etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
    ],
}


REQUEST_PIPELINE_FORM_VISAS = [
    # Pais
    {
        'name': 'Pais',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectPais',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectPais',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosSedes formRegistroCitaExtranjero:layoutMap formRegistroCitaExtranjero:panelSelectNoLegalizados formRegistroCitaExtranjero:panelnoPasapNUT formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelApellidos formRegistroCitaExtranjero:panelApellidoPat formRegistroCitaExtranjero:panelApellidoMat formRegistroCitaExtranjero:captcha formRegistroCitaExtranjero:panelDatosUsuario formRegistroCitaExtranjero formRegistroCitaExtranjero:panelSelectPaisNacimiento formRegistroCitaExtranjero:panelNacionalidad formRegistroCitaExtranjero:panelSelectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Documento
    {
        'name': 'Documento',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectTipoDocumento',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectTipoDocumento',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosSedes formRegistroCitaExtranjero:message formRegistroCitaExtranjero:layoutRegistroCitas matriculaConsularDialog formRegistroCitaExtranjero:panelSelectNoLegalizados formRegistroCitaExtranjero:panelnoPasapNUT formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelBotonesNut formRegistroCitaExtranjero:panelApellidos formRegistroCitaExtranjero:panelApellidoPat formRegistroCitaExtranjero:panelApellidoMat formRegistroCitaExtranjero formRegistroCitaExtranjero:panelSelectPaisNacimiento formRegistroCitaExtranjero:panelNacionalidad formRegistroCitaExtranjero:panelSelectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'formRegistroCitaExtranjero:selectSedeUbicacion_filter': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_focus': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_input': 4,
            'formRegistroCitaExtranjero:selectTramite_focus': '',
            'formRegistroCitaExtranjero:selectTramite_input': 'Selecciona...',
            'formRegistroCitaExtranjero:selectTipoTramite_focus': '',
            'formRegistroCitaExtranjero:selectTipoTramite_input': 'Selecciona...',
            'formRegistroCitaExtranjero:nombre': '',
            'formRegistroCitaExtranjero:ApellidoPat': '',
            'formRegistroCitaExtranjero:ApellidoMat': '',
            'formRegistroCitaExtranjero:fechaNacimiento_input': '',
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': '',
            'formRegistroCitaExtranjero:teldomicilio': '',
            'formRegistroCitaExtranjero:telmovil': '',
            # 'g-recaptcha-response': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Tramite
    {
        'name': 'Tramite',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectTramite',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectTramite',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosSedes formRegistroCitaExtranjero:panelSelectNoLegalizados formRegistroCitaExtranjero:panelnoPasapNUT formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelBotonesNut formRegistroCitaExtranjero formRegistroCitaExtranjero:panelSelectPaisNacimiento formRegistroCitaExtranjero:panelNacionalidad formRegistroCitaExtranjero:panelSelectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:selectTramite_focus': '',
            'formRegistroCitaExtranjero:selectTramite_input': 12,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Detalle
    {
        'name': 'Detalle',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectTipoTramite',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectTipoTramite',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosSedes formRegistroCitaExtranjero:panelSelectNoLegalizados formRegistroCitaExtranjero:panelnoPasapNUT formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelBotonesNut formRegistroCitaExtranjero formRegistroCitaExtranjero:panelSelectPaisNacimiento formRegistroCitaExtranjero:panelNacionalidad formRegistroCitaExtranjero:panelSelectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'formRegistroCitaExtranjero:selectSedeUbicacion_filter': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_focus': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_input': 4,
            'formRegistroCitaExtranjero:selectTramite_focus': '',
            'formRegistroCitaExtranjero:selectTramite_input': 12,
            'formRegistroCitaExtranjero:selectTipoTramite_focus': '',
            'formRegistroCitaExtranjero:selectTipoTramite_input': 63,
            'formRegistroCitaExtranjero:noPasapAnt': '',
            'formRegistroCitaExtranjero:selectPaisPasaporte_focus': '',
            'formRegistroCitaExtranjero:selectPaisPasaporte_input': 'Selecciona...',
            'formRegistroCitaExtranjero:nombre': '',
            'formRegistroCitaExtranjero:Apellidos': '',
            'formRegistroCitaExtranjero:selectNacionalidad_focus': '',
            'formRegistroCitaExtranjero:selectNacionalidad_input': 'Selecciona...',
            'formRegistroCitaExtranjero:fechaNacimiento_input': '',
            'formRegistroCitaExtranjero:selectPaisNacimiento_focus': '',
            'formRegistroCitaExtranjero:selectPaisNacimiento_input': 'Selecciona...',
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': '',
            'formRegistroCitaExtranjero:teldomicilio': '',
            'formRegistroCitaExtranjero:telmovil': '',
            # 'g-recaptcha-response': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # No. pasaporte
    {
        'name': 'Pasaporte',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:noPasapAnt',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:noPasapAnt',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelBotonesNut formRegistroCitaExtranjero:botonesBusqueda',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:noPasapAnt': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelnoPasapAnt"]'),
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelBotonesNut"]'),
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:botonesBusqueda"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Pais de emision de pasaporte
    {
        'name': 'Pais de emision de pasaporte',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectPaisPasaporte',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:selectPaisPasaporte_focus': '',
            'formRegistroCitaExtranjero:selectPaisPasaporte_input': 17,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Nombre
    {
        'name': 'Nombre',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:nombre',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:nombre',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelNombre',
            'javax.faces.behavior.event': 'blur',
            'javax.faces.partial.event': 'blur',
            'formRegistroCitaExtranjero:nombre': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelNombre"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Apellidos
    {
        'name': 'Apellidos',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:Apellidos',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:Apellidos',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelApellidos',
            'javax.faces.behavior.event': 'blur',
            'javax.faces.partial.event': 'blur',
            'formRegistroCitaExtranjero:Apellidos': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelApellidos"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Nacionalidad
    {
        'name': 'Nacionalidad',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectNacionalidad',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectNacionalidad',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:selectNacionalidad_focus': '',
            'formRegistroCitaExtranjero:selectNacionalidad_input': 49,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Fecha de nacimiento
    {
        'name': 'Fecha de nacimiento',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:fechaNacimiento',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:fechaNacimiento',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelFechaNacimiento',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:fechaNacimiento_input': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Pais de nacimiento
    {
        'name': 'Pais de nacimiento',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectPaisNacimiento',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectPaisNacimiento',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:selectPaisNacimiento_focus': '',
            'formRegistroCitaExtranjero:selectPaisNacimiento_input': 17,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Sexo
    {
        'name': 'Sexo',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:sexo',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:sexo',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelSexo',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': '',    # 0: HOMBRE, 1: MUJER
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelSexo"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Boton Buscar citas
    {
        'name': 'Boton Buscar citas',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:buscarCita',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero formRegistroCitaExtranjero:buscarCita formRegistroCitaExtranjero:layoutCalendarWeb',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero formRegistroCitaExtranjero:layoutCalendarWeb formRegistroCitaExtranjero:captcha',
            'formRegistroCitaExtranjero:buscarCita': 'formRegistroCitaExtranjero:buscarCita',
            'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'formRegistroCitaExtranjero:selectSedeUbicacion_filter': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_focus': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_input': 4,
            'formRegistroCitaExtranjero:selectTramite_focus': '',
            'formRegistroCitaExtranjero:selectTramite_input': 12,
            'formRegistroCitaExtranjero:selectTipoTramite_focus': '',
            'formRegistroCitaExtranjero:selectTipoTramite_input': 63,
            'formRegistroCitaExtranjero:noPasapAnt': '',
            'formRegistroCitaExtranjero:selectPaisPasaporte_focus': '',
            'formRegistroCitaExtranjero:selectPaisPasaporte_input': 17,
            'formRegistroCitaExtranjero:nombre': '',
            'formRegistroCitaExtranjero:Apellidos': '',
            'formRegistroCitaExtranjero:selectNacionalidad_focus': '',
            'formRegistroCitaExtranjero:selectNacionalidad_input': 49,
            'formRegistroCitaExtranjero:fechaNacimiento_input': '',
            'formRegistroCitaExtranjero:selectPaisNacimiento_focus': '',
            'formRegistroCitaExtranjero:selectPaisNacimiento_input': 17,
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': 0,
            'formRegistroCitaExtranjero:teldomicilio': '',
            'formRegistroCitaExtranjero:telmovil': '',
            'g-recaptcha-response': '',
            'javax.faces.ViewState': ''
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
        'validator_function': validate_response_button_buscar_citas,
    },
]


REQUEST_PIPELINE_FORM_CERTIFICADOS = [
    # Pais
    {
        'name': 'Pais',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'Faces-Request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'TE': 'Trailers',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectPais',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectPais',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosSedes formRegistroCitaExtranjero:layoutMap formRegistroCitaExtranjero:panelSelectNoLegalizados formRegistroCitaExtranjero:panelnoPasapNUT formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelApellidos formRegistroCitaExtranjero:panelApellidoPat formRegistroCitaExtranjero:panelApellidoMat formRegistroCitaExtranjero:captcha formRegistroCitaExtranjero:panelDatosUsuario formRegistroCitaExtranjero formRegistroCitaExtranjero:panelSelectPaisNacimiento formRegistroCitaExtranjero:panelNacionalidad formRegistroCitaExtranjero:panelSelectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Documento
    {
        'name': 'Documento',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectTipoDocumento',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectTipoDocumento',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosSedes formRegistroCitaExtranjero:message formRegistroCitaExtranjero:layoutRegistroCitas matriculaConsularDialog formRegistroCitaExtranjero:panelSelectNoLegalizados formRegistroCitaExtranjero:panelnoPasapNUT formRegistroCitaExtranjero:panelnoPasapAnt formRegistroCitaExtranjero:panelBotonesNut formRegistroCitaExtranjero:panelApellidos formRegistroCitaExtranjero:panelApellidoPat formRegistroCitaExtranjero:panelApellidoMat formRegistroCitaExtranjero formRegistroCitaExtranjero:panelSelectPaisNacimiento formRegistroCitaExtranjero:panelNacionalidad formRegistroCitaExtranjero:panelSelectPaisPasaporte',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'formRegistroCitaExtranjero:selectSedeUbicacion_filter': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_focus': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_input': 3,
            'formRegistroCitaExtranjero:selectTramite_focus': '',
            'formRegistroCitaExtranjero:selectTramite_input': 'Selecciona...',
            'formRegistroCitaExtranjero:selectTipoTramite_focus': '',
            'formRegistroCitaExtranjero:selectTipoTramite_input': 'Selecciona...',
            'formRegistroCitaExtranjero:nombre': '',
            'formRegistroCitaExtranjero:ApellidoPat': '',
            'formRegistroCitaExtranjero:ApellidoMat': '',
            'formRegistroCitaExtranjero:fechaNacimiento_input': '',
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': '',
            'formRegistroCitaExtranjero:teldomicilio': '',
            'formRegistroCitaExtranjero:telmovil': '',
            # 'g-recaptcha-response': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero"]'),
            etree.XPath('/partial-response/changes/update[@id="matriculaConsularDialog"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Numero documentos a legalizar
    {
        'name': 'Numero documentos a legalizar',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:selectNoLegalizados',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:selectNoLegalizados',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelDatosUsuario formRegistroCitaExtranjero:doc',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
            'formRegistroCitaExtranjero:selectNoLegalizados_focus': '',
            'formRegistroCitaExtranjero:selectNoLegalizados_input': 1,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Numero de MINREX
    {
        'name': 'Numero de MINREX',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:doc:0:noMinrex',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:doc:0:noMinrex',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:doc:0:panelnoMinrex',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:doc:0:noMinrex': 213,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:doc:0:panelnoMinrex"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Nombre
    {
        'name': 'Nombre',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:nombre',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:nombre',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelNombre',
            'javax.faces.behavior.event': 'blur',
            'javax.faces.partial.event': 'blur',
            'formRegistroCitaExtranjero:nombre': 'JOSE',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelNombre"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Primer apellido
    {
        'name': 'Primer apellido',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:ApellidoPat',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:ApellidoPat',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelApellidoPat',
            'javax.faces.behavior.event': 'blur',
            'javax.faces.partial.event': 'blur',
            'formRegistroCitaExtranjero:ApellidoPat': 'CASTILLO',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelApellidoPat"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Fecha nacimiento
    {
        'name': 'Fecha nacimiento',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:fechaNacimiento',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:fechaNacimiento',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelFechaNacimiento',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:fechaNacimiento_input': '15/05/1983',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelFechaNacimiento"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Sexo
    {
        'name': 'Sexo',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:sexo',
            'primefaces.resetvalues': 'true',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero:sexo',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero:panelSexo',
            'javax.faces.behavior.event': 'change',
            'javax.faces.partial.event': 'change',
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': 0,
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="formRegistroCitaExtranjero:panelSexo"]'),
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
    # Boton Buscar Cita
    {
        'name': 'Boton Buscar Cita',
        'method': 'POST',
        'url': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf',
        'request_headers': {
            'Accept': 'application/xml, text/xml, */*; q=0.01',
            'Accept-Language': 'es-US,es-419;q=0.9,es;q=0.8',
            'faces-request': 'partial/ajax',
            'Origin': 'https://mexitel.sre.gob.mx',
            'Referer': 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest',
        },
        'form_data': {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'formRegistroCitaExtranjero:buscarCita',
            'javax.faces.partial.execute': 'formRegistroCitaExtranjero formRegistroCitaExtranjero:buscarCita formRegistroCitaExtranjero:layoutCalendarWeb',
            'javax.faces.partial.render': 'formRegistroCitaExtranjero formRegistroCitaExtranjero:layoutCalendarWeb formRegistroCitaExtranjero:captcha',
            'formRegistroCitaExtranjero:buscarCita': 'formRegistroCitaExtranjero:buscarCita',
            'formRegistroCitaExtranjero': 'formRegistroCitaExtranjero',
            'formRegistroCitaExtranjero:selectPais_focus': '',
            'formRegistroCitaExtranjero:selectPais_input': 17,
            'formRegistroCitaExtranjero:selectSedeUbicacion_filter': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_focus': '',
            'formRegistroCitaExtranjero:selectTipoDocumento_input': 3,
            'formRegistroCitaExtranjero:selectNoLegalizados_focus': '',
            'formRegistroCitaExtranjero:selectNoLegalizados_input': 1,
            'formRegistroCitaExtranjero:doc:0:noMinrex': 213,
            'formRegistroCitaExtranjero:nombre': 'JOSE',
            'formRegistroCitaExtranjero:ApellidoPat': 'CASTILLO',
            'formRegistroCitaExtranjero:ApellidoMat': 'LORENZO',
            'formRegistroCitaExtranjero:fechaNacimiento_input': '15/05/1983',
            'formRegistroCitaExtranjero:sexo_focus': '',
            'formRegistroCitaExtranjero:sexo_input': 0,
            'formRegistroCitaExtranjero:teldomicilio': '',
            'formRegistroCitaExtranjero:telmovil': '53265689',
            'g-recaptcha-response': '',
            'javax.faces.ViewState': '',
        },
        'status_code': 200,
        'response_headers': {
            'content-type': 'text/xml',
        },
        'xml_valid_response': [
            etree.XPath('/partial-response/changes/update[@id="javax.faces.ViewState"]'),
        ],
        'xml_invalid_response': [
            etree.XPath('/partial-response/changes/extension[@ln="primefaces"]'),
        ],
    },
]