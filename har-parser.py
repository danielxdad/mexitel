# -*- coding: utf-8 -*-
# HAR parser de peticiones AJAX guardadas desde navegador
import argparse
import json
import pathlib
from urllib.parse import unquote

from colorama import Fore
from lxml import etree

import utils


def parse_argument() -> argparse.Namespace:
    """
    Parsea los parametros de la linea de comandos
    :return: Instancia de argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='HAR Parser')
    parser.add_argument('har_file', nargs=1, help='Fichero HAR')
    return parser.parse_args()


def main():
    args = parse_argument()

    har_file = pathlib.Path(args.har_file[0])
    if not har_file.exists():
        utils.print_message('[ERROR] - El fichero especificado no existe.', color=Fore.RED)
        return -1
    
    url = 'https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf'
    
    with har_file.open() as fd:
        har = json.load(fd)
        entries = har.get('log', []).get('entries', [])
        entries = list(filter(lambda e: e['request']['method'] == 'POST' and e['request']['url'].find(url) != -1, entries))
        # response = list(filter(lambda e: e['response']['content']['mimeType'] == 'text/xml'))
        # print(len(entries))
        for ent in entries:
            request = ent['request']
            post_data = request['postData']['params']
            response = ent['response']['content']['text']
            
            print(request['method'], request['url'])
            for header in request['headers']:
                if header['name'][0] != ':':
                    print('{}: {}'.format(header['name'], header['value']))
            print()
            
            for param in post_data:
                print('{}: {}'.format(unquote(param['name']), unquote(param['value']).replace('+', ' ')))
    
            print()
            # XML Response
            parser = etree.XMLParser(load_dtd=False, no_network=True, ns_clean=True, remove_comments=True)
            try:
                root = etree.fromstring(response.encode('UTF-8'), parser)
            except etree.ParseError as error:
                utils.print_message(
                    '[ERROR] - Parseando respuesta XML en utils.parse_calendar_data_month: "{}"'.format(error),
                    color=Fore.RED)
                return -1
            else:
                def iter_children(el):
                    # print('/%s' % el.tag, end='')
                    for ch in el:
                        if len(ch):
                            iter_children(ch)
                        else:
                            xpath = ['{}[{}]'.format(ch.tag, '&'.join(['@%s="%s"' % (attr, ch.attrib[attr]) for attr in ch.attrib]))]
                            parent = ch.getparent()
                            while parent is not None:
                                if len(parent.attrib):
                                    xpath.append('{}[{}]'.format(parent.tag, '&'.join(['@%s="%s"' % (attr, parent.attrib[attr]) for attr in parent.attrib])))
                                else:
                                    xpath.append('{}'.format(parent.tag))
                                parent = parent.getparent()
                    
                            xpath.reverse()
                            print('/' + '/'.join(xpath))
        
                iter_children(root)
    
            print('=' * 130, '\n')
            # input()
    

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print()
        exit()
