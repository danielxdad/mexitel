# -*- coding: utf-8 -*-
import os
import errno
import pathlib
import re
import glob
import warnings

import fitz
import numpy as np
from PIL import Image
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pytesseract
    import matplotlib.pyplot as plt

from config import PDF_TMP_IMAGES_DIR


def extract_pdf_images(doc, page=0, filter_dim=(229, 57)):
    """
    Extrea las imagenes y obtiene el "Codigo de seguridad" del documento PDF.
    :param doc: Instancia de documento PDF
    :param page: Numero de pagina(base 0) de la cual se extraeran las imagenes
    :param filter_dim: Tupla con las dimensiones(ancho, alto) para filtrar las imagenes
    :return: String con codigo de seguridad o dispara una excepcion en caso de error
    """
    # Si no existe el dictorio temporal para las imagenes, lo creamos
    if not os.path.exists(PDF_TMP_IMAGES_DIR):
        os.makedirs(PDF_TMP_IMAGES_DIR)

    # Eliminamos todas las imagenes PNG contenidas en el 
    for pn in pathlib.Path(PDF_TMP_IMAGES_DIR).glob('*.png'):
        pn.unlink()
    
    # Extraemos las imagenes en formato PNG
    imagen_found_count = 0
    for image in doc.getPageImageList(page):
        xref = image[0]
        width = image[2]
        height = image[3]

        # Si no corresponde el alto y el ancho con el declarado en filter_dimension no se guarda la imagen
        if (width, height) != filter_dim:
            continue

        # Convertimos la imagen a escala de grises
        pix = fitz.Pixmap(fitz.csGRAY, fitz.Pixmap(doc, xref))
        pix.writePNG(os.path.join(PDF_TMP_IMAGES_DIR, "page%s-%s.png" % (0, xref)))
        pix = None
        imagen_found_count += 1
    
    assert imagen_found_count == 2, 'Se encontraron {} imagenes para codigo de seguridad'.format(imagen_found_count)

    # Leemos las dos imagenes que deben tener el codigo
    image_list = []
    for pn in pathlib.Path(PDF_TMP_IMAGES_DIR).glob('*.png'):
        with pn.open('rb') as fd:
            image_list.append(plt.imread(fd, format='png').astype(np.uint8))
    
    assert image_list[0].shape == image_list[1].shape, 'Las dimensiones de las imagenes de codigo de seguridad son diferentes'
    
    xor_image_arr = np.bitwise_xor(image_list[0], image_list[1]).astype(np.uint8)
    # output_image_file = os.path.join(PDF_TMP_IMAGES_DIR, 'tesseract_image.png')
    # plt.imsave(output_image_file, xor_image_arr)
    # with Image.open(output_image_file) as fd:
    codigo_seg = pytesseract.image_to_string(xor_image_arr, config='-psm 8').strip()
    if not re.match('^[a-zA-Z0-9]{8}$', codigo_seg):
        raise ValueError('El codigo de seguridad es invalido: %s' % repr(codigo_seg))
    
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
    return (codigo_seg, text_token)


if __name__ == '__main__':
    # Test
    import sys
    import time
    
    if len(sys.argv) <= 1:
        print('[ERROR] - Especifica un PDF con los token!!!')
        exit()
        
    bt = time.time()
    codigo_seg, text_token = extract_pdf_tokens(sys.argv[1])

    print('Execute time: %.2f' % (time.time() - bt))
    print('Codigo seg:', codigo_seg)
    print('Token:', text_token)
