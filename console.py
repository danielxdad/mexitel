# -*- coding: utf-8 -*-
import os
import argparse
import time
import pathlib
import enum
import datetime
import random
import tkinter as tk
from http import HTTPStatus
from pprint import pprint


import requests
import pandas as pd
from lxml import etree
from colorama import Fore

import config
import cal
import peticiones
import utils
import mail
import pdf
import window_tk


class ActionEnum(enum.Enum):
    RELOGIN = 0
    CONTINUE = 1
    
    
def parse_argument() -> argparse.Namespace:
    """
    Parsea los parametros de la linea de comandos
    :return: Instancia de argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Mexitel fucker ;)')
    # parser.add_argument('--mes', nargs=1, type=str, choices=cal.MESES, help='Mes del calendario.')
    parser.add_argument('--anio', nargs=1, type=int, choices=cal.ANIOS, required=True, help='Anio del calendario.')
    parser.add_argument('--visas', action='store_true', help='Utilizar lista de acciones para Visas.')
    parser.add_argument('--no-confirm', action='store_true', help='No hacer la peticion de confirmacion de cita.')
    parser.add_argument('--emulate-relogin', action='store_true', help='Emula un relogin aleatorio desde la funcion calendar.')
    parser.add_argument('file', nargs=1, help='Fichero con datos de clientes.')
    return parser.parse_args()


def get_month_range():
    """
    Devuelve el rango de fechas de todo el año, la respuesta del servidor aunque solo se especifique un rango de mes
    viene con todos los eventos declarado en la pagina sin importar el rango especificado.
    :return: Tupla (mb, me)
    """
    args = parse_argument()
    
    # Dado que la respuesta XML para obtencion de rango fechas con disponibilidad en el calendario
    # es independiente de las especificadas en la peticion post obtemos el a;o entero
    mb = datetime.datetime(args.anio[0], 1, 1)
    me = datetime.datetime(args.anio[0], 12, 31)
    # me = datetime.datetime.combine(pd.date_range(mb, periods=1, freq='M').date[0], datetime.time(23, 59, 59))
    return mb, me


def detect_relogin_response(response: requests.Response) -> bool:
    """
    Detecta cuando el sitio a respondido para hacer relogin
    :param response: Instancia de requests.Response
    :return: Boolean True o False
    """
    if response.status_code == HTTPStatus.FOUND:
        utils.print_message('[INFO] - HTTP response: 302 Found')
        utils.print_message('[INFO] - HTTP response location: {}'.format(response.headers.get('location')))
        return True
    
    if response.status_code == HTTPStatus.OK:
        ct = response.headers['content-type']
        if ct.find('text/xml') != -1:
            parser = etree.XMLParser(load_dtd=False, no_network=True, ns_clean=True, remove_comments=True)
            try:
                root = etree.fromstring(response.content, parser)
            except etree.ParseError as error:
                utils.print_message('[ERROR] - Parseando respuesta XML: "{}"'.format(error), color=Fore.RED)
                return True
            else:
                for elname, xpath in [('redirect', '/partial-response[0]/redirect'),
                                      ('eval', '/partial-response[0]/eval'),
                                      ('error', '/partial-response[0]/error')]:
                    el = root.xpath(xpath)
                    if el:
                        utils.print_message('[INFO] - Detectado elemento "{}" en respuesta XML'.format(elname))
                        utils.print_message(el)
                        return True
    return False
    

def execute_action(peticion, ua, row, cookies, view_state) -> (ActionEnum, dict):
    """
    Ejecuta una accion(peticion)
    :param peticion: Diccionario que describe la accion(peticion)
    :return: Tupla con valor de ActionEnum y datos devueltos por funcion declarada en peticion['parser_response']
    """
    # Nombre de la accion
    name = peticion['name']

    # Cabeceras de peticion
    request_headers = peticion['request_headers']
    request_headers['User-Agent'] = ua

    # Datos del POST
    form_data = peticion['form_data']

    # ViewState
    form_data['javax.faces.ViewState'] = view_state

    # Pasaporte
    if 'formRegistroCitaExtranjero:noPasapAnt' in form_data:
        utils.print_message('[INFO] - Campo Pasaporte:', row['pasaporte'])
        form_data['formRegistroCitaExtranjero:noPasapAnt'] = row['pasaporte']

    # Nombre
    if 'formRegistroCitaExtranjero:nombre' in form_data:
        utils.print_message('[INFO] - Campo Nombre:', row['nombre'])
        form_data['formRegistroCitaExtranjero:nombre'] = row['nombre']

    # Apellidos
    if 'formRegistroCitaExtranjero:Apellidos' in form_data:
        utils.print_message('[INFO] - Campo Apellidos:', row['apellidos'])
        form_data['formRegistroCitaExtranjero:Apellidos'] = row['apellidos']

    # Fecha de nacimiento
    if 'formRegistroCitaExtranjero:fechaNacimiento_input' in form_data:
        utils.print_message('[INFO] - Campo Fecha de nacimiento:', row['fecha_nacimiento'])
        form_data['formRegistroCitaExtranjero:fechaNacimiento_input'] = row['fecha_nacimiento']

    # Sexo
    if 'formRegistroCitaExtranjero:sexo_input' in form_data:
        utils.print_message('[INFO] - Campo Sexo:', row['sexo'])
        form_data['formRegistroCitaExtranjero:sexo_input'] = row['sexo']

    # Telefono movil
    if 'formRegistroCitaExtranjero:telmovil' in form_data:
        utils.print_message('[INFO] - Campo Telefono movil:', row['telefono_movil'])
        form_data['formRegistroCitaExtranjero:telmovil'] = row['telefono_movil']
    
    # Captcha de Google
    if 'g-recaptcha-response' in form_data:
        captcha = None
        while not captcha:
            captcha = input(Fore.YELLOW + '[QUEST] - Introduce el CAPTCHA:').strip(' "')
        form_data['g-recaptcha-response'] = captcha
        
    # Calendario en modo mes
    if 'formRegistroCitaExtranjero:schedule_view' in form_data:
        if form_data['formRegistroCitaExtranjero:schedule_view'] == 'month':
            mb, me = get_month_range()
            form_data['formRegistroCitaExtranjero:schedule_start'] = int(mb.timestamp() * 1000)
            form_data['formRegistroCitaExtranjero:schedule_end'] = int(me.timestamp() * 1000)
    
    sleep_time = 0
    while True:
        if sleep_time > 0:
            utils.print_message('[INFO] - Esperando %d segundos para reintentar...' % sleep_time)
            time.sleep(sleep_time)
    
        data = None
        sleep_time = 10
    
        try:
            utils.print_message('[INFO] - Ejecutando accion "%s"...' % name)
            
            bt = time.time()
            response = requests.request(
                method=peticion['method'],
                url=peticion['url'],
                data=form_data,
                headers=request_headers,
                cookies=cookies,
                timeout=60,
                allow_redirects=False,
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
            utils.print_message('[INFO] - Tiempo de respuesta: %.2f seg' % (time.time() - bt))
            
            try:
                utils.response_to_file(response)
            except Exception as error:
                utils.print_message('[ERROR] - Excepcion al invocar utils.response_to_file: {}'.format(error), color=Fore.RED)
            
            if not response.ok:
                utils.print_message('[ERROR] - Error en respuesta de servidor: %d - %s' % (response.status_code, response.reason), color=Fore.RED)
                continue
        
            if detect_relogin_response(response):
                utils.print_message('[WARN] - Relogin detectado', color=Fore.LIGHTYELLOW_EX)
                return ActionEnum.RELOGIN, data
        
            if response.status_code != peticion['status_code']:
                utils.print_message('[ERROR] - El codigo HTTP es diferente al esperado: %d - %d' %
                      (response.status_code, peticion['status_code']), color=Fore.RED)
                continue
        
            header_ok = True
            for rh in peticion['response_headers']:
                rh_value = peticion['response_headers'][rh]
                if rh not in response.headers:
                    utils.print_message('[WARN] - No se encuentra la cabecera "%s" en la respuesta' % rh)
                    header_ok = False
                    continue
            
                if response.headers[rh].find(rh_value) == -1:
                    utils.print_message('[WARN] - No se encuentra el valor de testeo "%s" en cabecera "%s": "%s"'
                          % (rh_value, rh, response.headers[rh]))
                    header_ok = False
                    continue
        
            if not header_ok:
                continue
        
            # Si la comprobaciones anteriores estan correctas, interpretamos el XML que viene como respuesta
            parser = etree.XMLParser(load_dtd=False, no_network=True, ns_clean=True, remove_comments=True)
            try:
                root = etree.fromstring(response.content, parser)
            except etree.ParseError as error:
                utils.print_message('[ERROR] - Parseando respuesta XML: "{}"'.format(error), color=Fore.RED)
                continue
            else:
                xml_valid_response = True
                for xpath_func in peticion.get('xml_valid_response', []):
                    if not xpath_func(root):
                        utils.print_message('[ERROR] - No se puede encontrar el XPath "{}" en respuesta XML del servidor'.format(xpath_func),
                                            color=Fore.RED)
                        # print(etree.tostring(root, pretty_print=True, encoding='UTF-8').decode('UTF-8'))
                        xml_valid_response = False
                        break
            
                for xpath_func in peticion.get('xml_invalid_response', []):
                    lst = xpath_func(root)
                    if lst:
                        el = lst[0]
                        utils.print_message('[ERROR] - Se encuentra el XPath "{}" de error de validacion de datos: {}.'.format(
                            xpath_func, el.text), color=Fore.RED)
                        xml_valid_response = False
                        break
            
                if not xml_valid_response:
                    continue

                validator_funcion = peticion.get('validator_function', None)
                if validator_funcion:
                    if not validator_funcion(response):
                        continue
                        
                pr_function = peticion.get('parser_response', None)
                if pr_function:
                    data = pr_function(response)
            
                utils.print_message('[INFO] - Accion "%s" ejecutada correctamente' % name)
                utils.print_message('=' * 100, '\n')
                break
    
    return ActionEnum.CONTINUE, data


def calendar(ua, row, cookies, view_state) -> ActionEnum:
    """
    Funcion para procesamiento de eventos de calendario
    :param ua: User-Agent para enviar en la peticion
    :param row: Serie con datos de cliente
    :param cookies: Cookies a enviar en la peticion
    :param view_state: ViewState para enviar en la peticion
    :return: Valor de ActionEnum
    """
    print('[INFO] - Entrando en el Calendario...')

    availables_classes = ['rangoTotalDisponibilidad', 'rangoModerado', 'rangoAltaDisponibilidad']
    
    args = parse_argument()
    
    while True:
        # Obtenemos los eventos del calendario por mes
        action, data = execute_action(peticiones.CALENDAR_MONTH_REQUEST, ua, row, cookies, view_state)
        if action == ActionEnum.RELOGIN:
            return action
    
        # Filtramos los eventos de calendario que tengan disponibilidad y de dias posteriores a la fecha actual
        events = data.get('events', [])
        filtered_events = list(filter(lambda ev: ev.get('className') in availables_classes and
                                                 ev.get('start') > datetime.datetime.now(ev.get('start').tzinfo),
                                      events))
    
        utils.print_message('[INFO] - Total de eventos de calendario: %d' % len(events))
        utils.print_message('[INFO] - Eventos con disponibilidad: %d' % len(filtered_events))
    
        # Si no hay eventos en el calendario esperamos 20 segundos para refrescar
        if not filtered_events:
            # print(events)
            if args.emulate_relogin:
                if random.random() > 0.6:
                    utils.print_message('[INFO] - Emulando relogin', color=Fore.YELLOW)
                    return ActionEnum.RELOGIN
            time.sleep(20)
            continue
    
        event = random.choice(filtered_events)
        utils.print_message('[INFO] - Evento de calendario seleccionado:', color=Fore.LIGHTYELLOW_EX)
        pprint(event)
    
        # Hacemos la peticion para seleccionar el evento del calendario
        pet = peticiones.CALENDAR_MONTH_SELECT_EVENT.copy()
        pet['form_data']['formRegistroCitaExtranjero:schedule_selectedEventId'] = event['id']
        action, data = execute_action(pet, ua, row, cookies, view_state)
        if action == ActionEnum.RELOGIN:
            return action
    
        # Hacemos la peticion para obtener horas con disponibilidad en el evento(dia) seleccionado en la peticion
        # anterior
        schedule_start = event['start'].replace(hour=0, minute=0, second=0)
        schedule_end = event['start'].replace(hour=23, minute=59, second=59)
        pet = peticiones.CALENDAR_GET_DAY_EVENTS.copy()
        pet['form_data']['formRegistroCitaExtranjero:schedule_start'] = schedule_start
        pet['form_data']['formRegistroCitaExtranjero:schedule_end'] = schedule_end
        action, data = execute_action(pet, ua, row, cookies, view_state)
        if action == ActionEnum.RELOGIN:
            return action
    
        try:
            # Filtramos los eventos(horas) obtenidos que esten disponibles en el dia seleccionado anteriormente
            hour_event = random.choice(list(filter(lambda ev: ev.get('className') in availables_classes
                                                              and schedule_start < ev.get('start') < schedule_end,
                                                   data.get('events', []))))
        except (IndexError, ValueError):
            utils.print_message('[ERROR] - No se pudo obtener un evento de hora de calendario, '
                                'la lista de eventos esta vacia.',
                                color=Fore.RED)
            continue

        utils.print_message('[INFO] - Evento de hora de calendario seleccionado:', color=Fore.LIGHTYELLOW_EX)
        pprint(hour_event)
        
        # Hacemos la peticion para obtener email con PDF de Codigo de Seguridad y Token
        pet = peticiones.CALENDAR_SELECT_HOUR_EVENT.copy()
        pet['form_data']['formRegistroCitaExtranjero:schedule_selectedEventId'] = hour_event['id']
        action, data = execute_action(pet, ua, row, cookies, view_state)
        if action == ActionEnum.RELOGIN:
            return action
        
        # Esperamos maximo 180 segundos(3 minutos) por el arribo del correo
        nsegs = 180
        utils.print_message('[INFO] - Esperando por email PDF con "Codigo de seguridad" y "Token": %d minutos' % (nsegs // 60))
        message = mail.get_email_pdf_tokens(timeout=nsegs, filter_email_from='citas_sre@sre.gob.mx')
        if message:
            pdf_file_path = mail.save_pdf_from_message(message)
            codigo_seg, text_token = pdf.extract_pdf_tokens(pdf_file_path)
            utils.print_message('[INFO] - PDF: %s' % pdf_file_path)
    
            # Ventana para mostrar la imagen obtenida del "Codigo de seguridad" en el correo
            # y lo que se ha sacado por OCR para combrobar que esta bien
            if not os.path.exists(os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png')):
                utils.print_message('[ERROR] - La imagen "%s".' % os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png'),
                                    color=Fore.RED)
                return ActionEnum.CONTINUE
    
            root = tk.Tk()
            app = window_tk.Application(master=root,
                                        imagen=os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png'),
                                        text_ocr=codigo_seg)
            app.mainloop()
            codigo_seg = app.text_ocr.strip()
            
            utils.print_message('[INFO] - Codigo seguridad: %s' % codigo_seg)
            utils.print_message('[INFO] - Token: %s' % text_token)
    
            # Hacemos la peticion para confirmar la cita con el Codigo de Seguridad y Token
            if not args.no_confirm:
                pet = peticiones.CALENDAR_CONFIRM_CITA.copy()
                pet['form_data']['reviewForm:confirmCodigoSeguridad'] = codigo_seg
                pet['form_data']['reviewForm:confirmToken'] = text_token
                action, data = execute_action(pet, ua, row, cookies, view_state)
                if action == ActionEnum.RELOGIN:
                    return action
                
                utils.print_message('[INFO] - *** CITA CONFIRMADA ***', color=Fore.LIGHTWHITE_EX)
                break
            else:
                utils.print_message('[WARN] - No se confirma la cita por parametro "--no-confirm"',
                                    color=Fore.LIGHTYELLOW_EX)
        
        else:
            utils.print_message('[WARN] - Tiempo de espera agotado en obtencion de email con tokens', color=Fore.YELLOW)
            continue
        
    return ActionEnum.CONTINUE
        

def main():
    """
    Entry point function
    """
    args = parse_argument()
    
    excel_file = pathlib.Path(args.file[0])
    if not excel_file.exists():
        utils.print_message('[ERROR] - El fichero especificado no existe.', color=Fore.RED)
        return -1
    
    # Leemos el fichero Excel(XLS) con datos de clientes
    df = pd.read_excel(
        excel_file,
        converters={
            'fecha_nacimiento': lambda val: str(val),
            'telefono_movil': lambda val: str(val),
            'sexo': lambda val: 0 if val == 'HOMBRE' else 1,
            'procesado': str.upper,
        }
    )

    # Calculamos el rango de fechas del mes seleccionado en formato timestamp, restamos un dia al primer dia del mes
    # y sumamos un dia al ultimo
    mb, me = get_month_range()
    
    utils.print_message('[INFO] Parametros de ejecucion:')
    if args.visas:
        utils.print_message('\tCadena de acciones: VISAS')
        peticiones_pipeline = peticiones.REQUEST_PIPELINE_FORM_VISAS
    else:
        utils.print_message('\tCadena de acciones: CERTIFICADOS, LEGALIZACIONES Y VISADOS')
        peticiones_pipeline = peticiones.REQUEST_PIPELINE_FORM_CERTIFICADOS
    
    utils.print_message('\tRango de calendario: {}({}) - {}({})'.format(mb.date(), int(mb.timestamp() * 1000),
                                                          me.date(), int(me.timestamp() * 1000)))
    utils.print_message('\tCuenta de acceso:', config.USERNAME)
    utils.print_message('\tCuenta de correo:', config.EMAIL_ACCOUNT)
    utils.print_message('=' * 100, '\n')
    
    ua = 'Mozilla/5.0 Gecko/20100101 Firefox/65.0'
    action = ActionEnum.RELOGIN
    cookies, view_state = None, None
    
    while True:
        if df[df.procesado == 'NO'].empty:
            utils.print_message('[INFO] - No hay registros de clientes por procesar.')
            break
            
        if action == ActionEnum.RELOGIN or not cookies or not view_state:
            cookies, view_state = utils.get_login_new_cookie(user_agent=ua)
            if not cookies or not view_state:
                return False
            print('=' * 100, '\n')
    
        for index, row in df.iterrows():
            if row['procesado'].lower() != 'no':
                continue
        
            utils.print_message('[INFO] - Procesando registro {} - {} {}...'.format(index + 1, row['nombre'], row['apellidos']))
            
            for peticion in peticiones_pipeline:
                action, data = execute_action(peticion, ua, row, cookies, view_state)
                if action == ActionEnum.RELOGIN:
                    break
        
            if action == ActionEnum.RELOGIN:
                break
            
            # Aqui estamos en el calendario
            if action == ActionEnum.CONTINUE:
                action = calendar(ua, row, cookies, view_state)
                if action == ActionEnum.RELOGIN:
                    break
                    
            val = input('[INFO] - El registro {} - "{} {}" ha sido procesado? (si/no):'.format(
                index + 1, row['nombre'], row['apellidos'])).lower()
            if val == 'si':
                df.loc[index, 'procesado'] = 'SI'
        
    # Actualizamos los registros en el fichero Excel que hayan sido procesados correctamente
    with pd.ExcelWriter(str(excel_file.resolve())) as writer:
        df.to_excel(writer, index=False)
    
    utils.print_message('[INFO] - Cerrando...')
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print()
        exit(0)
