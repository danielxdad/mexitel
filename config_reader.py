# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from configparser import ConfigParser


def read_config(config_file, section):
    """
    Lee la configuracion de la seccion del archivo INI especificado
    :param config_file: Archivo de configuracion con informacion sensible
    :param section: Seccion a leer desde el archivo de configuracion
    :return: Diccionario con los valores y datos de la seccion espeficada
    """
    cfgp = ConfigParser()
    with open(config_file, 'r') as fp:
        cfgp.read_file(fp)
        d = dict(cfgp.items(section))
    return d
