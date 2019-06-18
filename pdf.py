# -*- coding: utf-8 -*-
import os
import errno
import pathlib
import re
import warnings

import fitz
import numpy as np
from colorama import Fore
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pytesseract
    import matplotlib.pyplot as plt

import config
import utils


def extract_pdf_images(doc, page=0):
    """
    Extrea las imagenes y obtiene el "Codigo de seguridad" del documento PDF.
    :param doc: Instancia de documento PDF
    :param page: Numero de pagina(base 0) de la cual se extraeran las imagenes
    :return: String con codigo de seguridad o dispara una excepcion en caso de error
    """
    # Si no existe el dictorio temporal para las imagenes, lo creamos
    if not os.path.exists(config.PDF_TMP_IMAGES_DIR):
        os.makedirs(config.PDF_TMP_IMAGES_DIR)
    
    # Eliminamos todas las imagenes PNG contenidas en el 
    for pn in pathlib.Path(config.PDF_TMP_IMAGES_DIR).glob('*.png'):
        pn.unlink()
    
    # Extraemos las imagenes en formato PNG
    imagen_found_count = 0
    for image in doc.getPageImageList(page):
        xref = image[0]
        width = image[2]
        height = image[3]
        
        # Si no corresponde el alto y el ancho con el declarado en filter_dimension no se guarda la imagen
        # Resoluciones obtenidas en pruebas de imagen con "Codigo de seguridad":
        # 209x57, 229x57, 235x57, 265x57
        # if not(200 <= width <= 265 and height == 57):
        #     continue
        
        # Hora picotean el codigo de seguridad por cada letra, la altura de la imagen se mantiene en 57
        # Ancho minimo 16, maximo 47
        if not(10 <= width <= 50 and height == 57):
            continue
        
        # Convertimos la imagen a escala de grises
        pix = fitz.Pixmap(fitz.csGRAY, fitz.Pixmap(doc, xref))
        pix.writePNG(os.path.join(config.PDF_TMP_IMAGES_DIR, "%s.png" % xref))
        imagen_found_count += 1
    
    assert imagen_found_count == 16, 'Se encontraron {} imagenes para codigo de seguridad, no 16.'.format(imagen_found_count)
    
    # Leemos las dos imagenes que deben tener el codigo
    image_peer = []
    csimage = None
    for pn in sorted(pathlib.Path(config.PDF_TMP_IMAGES_DIR).glob('*.png'), key=lambda p: int(p.stem)):
        if len(image_peer) == 2:
            with image_peer[0].open('rb') as fd:
                img1 = plt.imread(fd, format='png')#.astype(np.uint8)
                
            with image_peer[1].open('rb') as fd:
                img2 = plt.imread(fd, format='png')#.astype(np.uint8)
                
            image_peer = []
            
            try:
                # comb_image = np.bitwise_xor(img1, img2)
                comb_image = np.subtract(img1, img2)
                comb_image[comb_image < 1] = 0
            except ValueError as err:
                utils.print_message('[ERROR] - Error combinando las imagenes "{}" y "{}": {}'.format(
                    image_peer[0], image_peer[1], err), color=Fore.RED)
                return ''
            else:
                # fig, axs = plt.subplots(1, 3)
                # images = [img1, img2, comb_image]
                # for i in range(3):
                #     img, ax = images[i], axs[i]
                #     ax.imshow(img, cmap=plt.cm.gray)
                #     ax.axis('off')
                # plt.show()
                
                if csimage is None:
                    csimage = comb_image
                else:
                    csimage = np.hstack((csimage, comb_image))
            
        image_peer.append(pn)

    output_image_file = os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png')
    plt.imsave(output_image_file, csimage, cmap=plt.cm.gray)
    codigo_seg = pytesseract.image_to_string(csimage, config='-psm 8').strip()
    
    # assert image_list[0].shape == image_list[1].shape,
    # 'Las dimensiones de las imagenes de codigo de seguridad son diferentes'
    # xor_image_arr = np.bitwise_xor(image_list[0], image_list[1]).astype(np.uint8)
    # output_image_file = os.path.join(config.PDF_TMP_IMAGES_DIR, 'tesseract_image.png')
    # plt.imsave(output_image_file, xor_image_arr)
    # codigo_seg = pytesseract.image_to_string(xor_image_arr, config='-psm 8').strip()
    # if not re.match('^[a-zA-Z0-9]{8}$', codigo_seg):
    # raise ValueError('El codigo de seguridad es invalido: %s' % repr(codigo_seg))
    
    # fig, axs = plt.subplots(3, 1)
    # images = image_list + [xor_image_arr]
    # for i in range(3):
    # img, ax = images[i], axs[i]
    # ax.imshow(img, cmap=plt.cm.gray)
    # ax.axis('off')
    # plt.show()
    
    return codigo_seg


def extract_pdf_tokens(pdf_file_path):
    """
    Extrea el "Codigo de seguridad" y el "Token" del documento PDF especificado.
    :param pdf_file_path: Path del documento PDF
    :return: Tupla con el "Codigo de seguridad" y el "Token"
    """
    pdf_file = pathlib.Path(pdf_file_path)
    if not pdf_file.exists():
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT))
    
    doc = fitz.open(pdf_file.resolve())
    
    # Test pagecount & metadata
    assert doc.pageCount == 1, 'Cantidad de paginas del PDF > 1'
    for key, val in (('format', 'PDF 1.4'), ('creator', 'JasperReports Library version 5.5.2'), 
        ('producer', 'iText 2.1.7 by 1T3XT')):
        assert key in doc.metadata, 'La clave "{}" no se encuentra en los metadata del PDF'.format(key)
        assert val == doc.metadata[key], 'El valor de la "{}" no se igual que en los metadata del PDF'.format(key)

    page = doc.loadPage(0)
    
    # Test search text
    for text in ['Notificación de información para Código de Seguridad y Token', 'Código Seguridad:', 'Token:']:
        if not page.searchFor(text, hit_max=1):
            raise ValueError('No se pudo encontrar la sentencia en el PDF: "{}"'.format(text))
    
    # Token text search
    regexp_token = re.compile(r'^[\w\/\-\+\*\=\.\$]{64}$')
    text_token = None
    for line in page.getText("text").split('\n'):
        if regexp_token.match(line):
            text_token = line
            break
    
    if not text_token:
        raise ValueError('No se pudo encontrar el token de texto en el PDF.')
    
    codigo_seg = extract_pdf_images(doc)
    doc.close()
    return codigo_seg, text_token


if __name__ == '__main__':
    # Test
    import sys
    import time
    import tkinter as tk
    import window_tk
    
    if len(sys.argv) <= 1:
        print('[ERROR] - Especifica un PDF con los token!!!')
        exit()
        
    bt = time.time()
    codigo_seg, text_token = extract_pdf_tokens(sys.argv[1])

    print('Execute time: %.2f' % (time.time() - bt))
    print('Codigo seg:', codigo_seg)
    print('Token:', text_token)

    root = tk.Tk()
    app = window_tk.Application(master=root, imagen='pdf/images/tesseract_image.png', text_ocr=codigo_seg)
    app.mainloop()
    print('Codigo seg:', app.text_ocr)
