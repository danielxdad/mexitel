# -*- coding: utf-8 -*-
import os
import datetime
import time
import random
import re
import tkinter as tk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    MoveTargetOutOfBoundsException

import config
import mail
import pdf
import window_tk


MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 
        'septiembre', 'octubre', 'noviembre', 'diciembre']

ANIOS = list(range(datetime.date.today().year, datetime.date.today().year + 2))


def _search_cal_header(driver):
    """
    Devuelve una lista con los elementos "boton Atras", "Titulo(H2)" y "boton Adelante" del header del calendario 
    :param driver: Instancia de driver de navegador
    :return: WebElement o None
    """
    xpath_list = ['//*[@id="formRegistroCitaExtranjero:schedule_container"]/div[1]/div[1]/button', 
        '//*[@id="formRegistroCitaExtranjero:schedule_container"]/div[1]/div[3]/h2', 
        '//*[@id="formRegistroCitaExtranjero:schedule_container"]/div[1]/div[2]/button']
    elements = []
    for xpath in xpath_list:
        try:
            elements.append(driver.find_element(By.XPATH, xpath))
        except NoSuchElementException:
            print('[ERROR] - No se puede encontrar el "%s" del calendario.' % xpath)
            return (None, None, None)
    return elements


def _go_to_month(driver, mes, anio):
    """
    Mueve el calendario al mes/anio especificado
    :param driver: Instancia de driver de navegador
    :param mes: Mes en el cual se buscara la disponibilidad: "Mayo"
    :param anio: Anio en el cual se buscar la disponibilidad: "2019"
    """
    driver.execute_script("window.scrollTo(0, 0);")

    # Importamos esto aqui ;)
    from main import check_procesing_modal

    # Buscamos los botones de Adelante y Atras y el H2 con el mes y anio en la cabecera del calendario
    el_cal_button_backward, el_cal_header, el_cal_button_forward = _search_cal_header(driver)
    if not el_cal_button_backward or not el_cal_header or not el_cal_button_forward:
        return False

    mes = mes.lower()
    header_month, header_year = el_cal_header.text.strip().lower().split(' ')

    try:
        header_year = int(header_year)
    except (ValueError, TypeError):
        print('[ERROR] - El mes o el anio en el header del calendario no es valido: "{} {}"'.format(header_month, header_year))
        return False

    if header_month not in MESES or header_year not in ANIOS:
        print('[ERROR] - El mes o el anio en el header del calendario no es valido: "{} {}"'.format(header_month, header_year))
        return False

    # Obtenemos los indices del mes y anio del calendario y del parametro mes y anio
    hm_index = MESES.index(header_month)
    hy_index = ANIOS.index(header_year)
    mes_index = MESES.index(mes)
    anio_index = ANIOS.index(anio)

    while hy_index != anio_index or hm_index != mes_index:
        # Si el anio en que esta el calendario es menor que el especificado
        if hy_index < anio_index:
            el_cal_button_forward.click()   # Damos click en el boton Adelante
            time.sleep(0.4)                 # Esperamos 0.5 segundos
            check_procesing_modal(driver)   # Chequemos el modal "Procesando..."
        # Si el anio en que esta el calendario es mayor que el especificado
        elif hy_index > anio_index:
            el_cal_button_backward.click()  # Damos click en el boton Atras
            time.sleep(0.4)                 # Esperamos 0.5 segundos
            check_procesing_modal(driver)   # Chequemos el modal "Procesando..."
        # Si los dos anios son iguales, chequeamos los meses
        else:
            if hm_index < mes_index:
                el_cal_button_forward.click()   # Damos click en el boton Adelante
                time.sleep(0.4)                 # Esperamos 0.5 segundos
                check_procesing_modal(driver)   # Chequemos el modal "Procesando..
            elif hm_index > mes_index:
                el_cal_button_backward.click()  # Damos click en el boton Atras
                time.sleep(0.4)                 # Esperamos 0.5 segundos
                check_procesing_modal(driver)   # Chequemos el modal "Procesando..."
            else:
                return True
        
        # Volvemos a coger los valores de Mes/Anio del calendario
        header_month, header_year = el_cal_header.text.strip().lower().split(' ')
        try:
            header_year = int(header_year)
        except (ValueError, TypeError):
            print('[ERROR] - El mes o el anio en el header del calendario no es valido: "{} {}"'.format(header_month, header_year))
            return False

        if header_month not in MESES or header_year not in ANIOS:
            print('[ERROR] - El mes o el anio en el header del calendario no es valido: "{} {}"'.format(header_month, header_year))
            return False

        hm_index = MESES.index(header_month)
        hy_index = ANIOS.index(header_year)
    
    return True


def calendar(driver, mes, anio):
    """
    Funcion que hara el trabajo del calendario. 
    :param driver: Instancia de driver de navegador
    :param mes: Mes en el cual se buscara la disponibilidad: "Mayo"
    :param anio: Anio en el cual se buscar la disponibilidad: "2019"
    :return: Boolean
    """
    # Importamos esto aqui ;)
    from main import check_procesing_modal
    print('[INFO] - Haciendo la magia del calendario...')
    
    # Hacemos un cicho
    a_tags_elements = []
    while not a_tags_elements:
        if not _go_to_month(driver, mes, anio):
            return False

        # Buscamos tags A que dice la cantidad de citas disponibles por dia clases css
        a_tags_css_selectors = ['a.fc-day-grid-event.fc-event.fc-start.fc-end.rangoTotalDisponibilidad', 
            'a.fc-day-grid-event.fc-event.fc-start.fc-end.rangoModerado',
            'a.fc-day-grid-event.fc-event.fc-start.fc-end.rangoAltaDisponibilidad']
        
        for css_sel in a_tags_css_selectors:
            a_tags_elements += driver.find_elements_by_css_selector(css_sel)
        
        # Si no se encontraron tags A para dias con disponibildad en el calendario, 
        # damos click en el boton "Mes" para refrescar el calendario en el mes actual seleccionado
        # para ver si ya abrieron las citas
        if not a_tags_elements:
            # Boton Mes, ID: "formRegistroCitaExtranjero:Month"
            try:
                el = driver.find_element_by_id('formRegistroCitaExtranjero:Month')
            except NoSuchElementException:
                print('[ERROR] - No existe el boton "Mes" en el calendario.')
                return False
            else:
                driver.execute_script("window.scrollTo(0, 0);")
                el.click()
                time.sleep(0.5)
                check_procesing_modal(driver)
                time.sleep(0.8)
        else:
            break
        
        # Hacemos una espera de 15 segundos entre cada refresqueo del calendario
        time.sleep(15)
            
    # Si no se encontraron tags A para dias con disponibildad en el calendario
    if not a_tags_elements:
        # Mostramos mensaje de error y devolvemos false
        print('[ERROR] - No se encontraron dias con disponibildad en el calendario.')
        return False
    
    # Tomamos uno de los tags A de dias con disponibilidad aleatoriamente
    a_element = random.choice(a_tags_elements)
    
    # Damos click en el tag A para acceder a ese dia, hacemos un tiempo de espera 
    # y chequemos la aparacion del modal "Procesando..."
    driver.execute_script("window.scrollTo(0, %d);" % (a_element.location['y'] - 200))
    a_element.click()
    time.sleep(0.5)
    check_procesing_modal(driver)

    # Aqui estamos en el calendario en modo Agenta/Dia
    el_cal_button_backward, el_cal_header, el_cal_button_forward = _search_cal_header(driver)
    if not el_cal_button_backward or not el_cal_header or not el_cal_button_forward:
        return False

    # Testeamos el titulo(H2) del calendario con formato: "Mayo 23, 2019"
    title = el_cal_header.text.strip()
    if not re.match(r'[\w]{4,10} [\d]{1,2}, [\d]{4}', title):
        print('[ERROR] - El valor del titulo de calendario no corresponde con el formato de dias: {}'.format(title))
        return False

    # Buscamos los tags A que especifica la hora de disponibilidad de la cita: "9:00 - 7 disponibles"
    a_tags_css_selectors = ['a.fc-time-grid-event.fc-event.fc-start.fc-end.rangoAltaDisponibilidad.fc-short', 
        'a.fc-time-grid-event.fc-event.fc-start.fc-end.rangoModerado.fc-short', 
        'a.fc-time-grid-event.fc-event.fc-start.fc-end.rangoTotalDisponibilidad.fc-short']
    a_tags_elements = []
    for css_sel in a_tags_css_selectors:
        a_tags_elements += driver.find_elements_by_css_selector(css_sel)

    # Si no se encontraron tags A para dias con disponibildad en el calendario
    if not a_tags_elements:
        # Mostramos mensaje de error y devolvemos false
        print('[ERROR] - No se encontraron horas con disponibildad en el dia seleccionado.')
        return False
    
    # Tomamos uno de los tags A de hora con disponibilidad aleatoriamente y le damos click
    a_element = random.choice(a_tags_elements)
    driver.execute_script("window.scrollTo(0, %d);" % (a_element.location['y'] - 200))
    a_element.click()
    time.sleep(0.5)
    check_procesing_modal(driver)

    # Obtenemos email con PDF con el Codigo de seguridad y Token, esperamos 90 segundos a su llegada.
    message = mail.get_email_pdf_tokens(timeout=90, filter_email_from='citas_sre@sre.gob.mx')
    if message:
        pdf_file_path = mail.save_pdf_from_message(message)
        codigo_seg, text_token = pdf.extract_pdf_tokens(pdf_file_path)
        print('[INFO] - PDF: %s' % pdf_file_path)
        print('[INFO] - Codigo seguridad: %s' % codigo_seg)
        print('[INFO] - Token: %s' % text_token)
        
        # Ventana aparte del navegador para mostrar la imagen obtenida del "Codigo de seguridad" en el correo 
        # y lo que se ha sacado por OCR para combrobar que esta bien
        if not os.path.exists(os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png')):
            print('[ERROR] - La imagen "%s".' % os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png'))
            return False

        root = tk.Tk()
        app = window_tk.Application(master=root, 
            imagen=os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png'), 
            text_ocr=codigo_seg)
        app.mainloop()
        codigo_seg = app.text_ocr.strip()

        # Buscamos el modal con la informacion de la cita y los campos para Codigo de seguridad y Token
        # y testeamos que sea visible
        try:
            el_modal = driver.find_element_by_id('confirmDialog')
        except NoSuchElementException:
            print('[ERROR] - No se ha podido encontrar el modal "Detalle de la cita".')
            return False
        
        if not el_modal.is_displayed():
            print('[ERROR] - El modal "Detalle de la cita" no es visible al usuario.')
            return False
        
        # Buscamos el campo INPUT Codigo de seguridad y INPUT Token para establecerle los valores
        try:
            el_input_cod_seg = driver.find_element_by_id('reviewForm:confirmCodigoSeguridad')
        except NoSuchElementException:
            print('[ERROR] - No se ha podido encontrar el campo "Codigo de seguridad" en el modal "Detalle de la cita".')
            return False
        else:
            # Hacemos un scroll al elemento
            driver.execute_script('document.getElementById("{}").scrollIntoView(false)'.format('reviewForm:confirmCodigoSeguridad'))
            time.sleep(0.2)
            el_input_cod_seg.click()
            time.sleep(0.2)
            el_input_cod_seg.send_keys(codigo_seg)
        
        try:
            el_input_token = driver.find_element_by_id('reviewForm:confirmToken')
        except NoSuchElementException:
            print('[ERROR] - No se ha podido encontrar el campo "Token" en el modal "Detalle de la cita".')
            return False
        else:
            # Hacemos un scroll al elemento
            driver.execute_script('document.getElementById("{}").scrollIntoView(false)'.format('reviewForm:confirmToken'))
            time.sleep(0.2)
            el_input_token.click()
            time.sleep(0.2)
            el_input_token.send_keys(text_token)

        # Buscamos el boton de confirmar la cita
        try:
            el_button_confirm = driver.find_element_by_id('reviewForm:confirmarCita')
        except NoSuchElementException:
            print('[ERROR] - No se ha podido encontrar el boton "Confirmar cita" en el modal "Detalle de la cita".')
            return False
        else:
            # Hacemos un scroll al elemento
            driver.execute_script('document.getElementById("{}").scrollIntoView(false)'.format('reviewForm:confirmarCita'))
            time.sleep(0.2)
            el_button_confirm.click()
            time.sleep(0.5)
            check_procesing_modal(driver)
            time.sleep(0.5)
        
        # TODO: Mejorar comprobacion de este modal ya que puede demorarse en salir debido a carga de la pagina
        time.sleep(3)
        try:
            # Testeamos la aparacicion del modal "Has concluido tu tramite", ID: "#j_idt427"
            el_modal = driver.find_element_by_id('j_idt427')
        except NoSuchElementException:
            print('[ERROR] - No se ha podido encontrar el modal "Has concluido tu tramite".')
            return False
        else:
            time.sleep(1.5)
            if not el_modal.is_displayed():
                print('[ERROR] - El modal "Has concluido tu tramite" no esta visible para el usuario.')
                return False
            
            # Testeamos el titulo del modal
            el_modal_title = driver.find_element_by_id('j_idt427_title')
            if el_modal_title.text.strip().find('Has concluido tu trámite') == -1:
                print('[ERROR] - El titulo del modal "Has concluido tu tramite" no corresponde con "Has concluido tu trámite"')
                return False
    else:
        print('[WARN] - Tiempo de espera agotado en obtencion de email con tokens.')
        return False
    
    # Si llegamos aqui tenemos una en la buchaca XD
    print('[INFO] - Se ha confirmado una cita en el calendario.')
    return True
