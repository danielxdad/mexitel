# -*- coding: utf-8 -*-
import os
import imaplib
import socket
import time
import datetime
import email
import email.header
import email.headerregistry
import email.message
import email.policy

import config


def parse_email(email_message):
    """
    Parsea un las cabeceras y el cuerpo del correo electronico de respuesta de servidor IMAP
    :param email_message: Cabeceras y cuerpo del mensaje
    :return: Instancia de email.message.Message
    """
    headers, body = email_message
    message = email.message_from_bytes(body, email.message.EmailMessage)
    return message


def decode_header(header):
    """
    Decodifica una cabecera de un correo
    :param header: Valor del header a decodificar
    :return: String con valor decodificado 
    """
    val, charset = email.header.decode_header(header)[0]
    if charset:
        return val.decode(charset)
    return val


def filter_email_message(message, filter_email_from):
    """
    Filtra el correo electronico recibido segun cabecera "From", "Subject"
    :param message: Instancia de email.message.Message
    :param filter_email_from: Direccion de correo electronico del remitente
    return: Parametro message o None si a pasado el filtro o no
    """
    message_subject = 'Notificación Citas SRE: Código Seguridad y Token'
    return message['From'].find(filter_email_from) != -1 and decode_header(message['Subject']).find(message_subject) != -1


def get_email_pdf_tokens(timeout=120, filter_email_from='citas_sre@sre.gob.mx'):
    """
    Obtiene el email con el PDF con el Token y Codigo de seguridad para validacion de cita en el calendario de MEXITEL.
    :param timeout: Tiempo de espera para obtencion de correos
    :param filter_email_from: Correo remitente utilizado en filtrado de los correos
    :return: Instancia email.message.EmailMessage con el PDF o None en caso de no haberlo encontrado
    """
    # Leemos los UIDs de los correos que ya han sido procesados anteriormente
    procesed_uids = []
    with open(config.FILE_EMAIL_UID_REG, 'r') as fd:
        for line in fd:
            if not line:
                break
            procesed_uids.append(line.strip())
    
    # Nos conectamos al servidor IMAP
    timeout_interval = 3
    for _ in range(timeout // timeout_interval):
        try:
            M = imaplib.IMAP4_SSL(config.EMAIL_HOST)
        except socket.timeout:
            print('[ERROR] - Tiempo de espera agatado conectando con el servidor de correo.')
            return None
        except socket.error as err:
            print('[ERROR] - Error conectando con el servidor de correo: {}'.format(err))
            return None

        # Nos logeamos
        M.login(config.EMAIL_ACCOUNT, config.EMAIL_PASSWORD)
        # Se selecciona el mailbox INBOX para solo lectura
        M.select(mailbox='INBOX', readonly=True)
    
        typ, data = M.uid('SEARCH', None, '(FROM "{}")'.format(filter_email_from))
        
        if typ != 'OK':
            print('[ERROR] - Error obteniendo lista de emails: {}'.format(data))
            break

        for uid in data[0].split():
            uid = uid.decode('utf-8')

            if uid in procesed_uids:
                print('[INFO] - El email "{}" ya ha sido procesado, se ignora.'.format(uid))
                continue

            print('[INFO] - Obteniendo email "{}"...'.format(uid))
            typ, data = M.uid('FETCH', uid, '(RFC822)')
            
            # Agregamos el UID de correo a fichero de registro de UIDs procesados
            procesed_uids.append(uid.strip())
            with open(config.FILE_EMAIL_UID_REG, 'a') as fd:
                fd.write('%s\n' % uid)
            
            if typ != 'OK':
                print('[ERROR] - Error obteniendo email {}: {}'.format(uid, data))
                break
            else:
                message = parse_email(data[0])
                subject = decode_header(message['Subject'])
                if not filter_email_message(message, filter_email_from):
                    print('[INFO] - El email {} - "{}" no ha pasado el filtro de mensajes.'.format(uid, subject))
                else:
                    # Itineramos por los adjuntos del correo y si tiene el pdf "CodigoSeguridadCita.pdf" y devolvemos el mensaje
                    for subpart in message.iter_attachments():
                        attach_file_name, attach_content_type = subpart.get_filename(''), subpart.get_content_type()
                        if attach_file_name == 'CodigoSeguridadCita.pdf' and attach_content_type == 'application/pdf':
                            M.close()
                            M.logout()
                            print('[INFO] - OK email codigo seguridad & token:', uid, subject)
                            return message
        
        M.close()
        M.logout()

        print('[INFO] - Esperando por arrivo de correo...')
        time.sleep(timeout_interval)
    
    return None


def save_pdf_from_message(message):
    """
    Guarda el PDF adjunto en el mensaje en el direction espeficiado en config.PDF_TMP_DIR.
    :param message: Instancia de email.message.EmailMessage
    :return: Path a fichero PDF o None 
    """
    file_path = None
    for subpart in message.iter_attachments():
        attach_file_name, attach_content_type = subpart.get_filename(''), subpart.get_content_type()
        if attach_file_name == 'CodigoSeguridadCita.pdf' and attach_content_type == 'application/pdf':
            payload = subpart.get_payload(decode=True)
            new_name = 'CodigoSeguridadCita-{}.pdf'.format(int(datetime.datetime.now().timestamp() * 1000))
            file_path = os.path.join(config.PDF_TMP_DIR, new_name)
            with open(file_path, 'wb') as fd:
                fd.write(payload)
    
    return file_path


if __name__ == '__main__':
    # Test mail
    try:
        """
        uid = '40200'
        with open('/home/daniel/Fwd_ Notificación Citas SRE_ Código Seguridad y Token.eml', 'rb') as fd:
            message = email.message_from_binary_file(fd, email.message.EmailMessage)
        filter_email_from = 'danielxdad@gmail.com'
        subject = decode_header(message['Subject'])
        if not filter_email_message(message, filter_email_from):
            print('[INFO] - El email {} - "{}" no ha pasado el filtro de mensajes.'.format(uid, subject))
        else:
            # TODO: Extraer el PDF con el Token y Codigo de seguridad
            print('OK', uid, subject)
            pdf_file_path = save_pdf_from_message(message)
            print(pdf_file_path)
        """
        message = get_email_pdf_tokens(timeout=120, filter_email_from='citas_sre@sre.gob.mx')
        if message:
            from pdf import extract_pdf_tokens
            pdf_file_path = save_pdf_from_message(message)
            codigo_seg, text_token = extract_pdf_tokens(pdf_file_path)
            print('Codigo seg:', codigo_seg)
            print('Token:', text_token)
        else:
            print('[WARN] - Tiempo de espera agotado en obtencion de email con tokens.')

    except KeyboardInterrupt:
        pass
    exit(0)
