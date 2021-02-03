# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>

# splprocessor.py

# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
# be included in the file GPL-3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU Library General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

""" 
splwatcher
==========

**splwatcher**, es el monitor y procesador de archivos de colas de impresión
(spool) del proyecto **OpenErm**. Su trabajo constiste en:

    * Monitorear una o más carpetas
    * Detectar nuevos archivos en estas
    * Detectar por patrones regulares nombres de archivo a procesar
    * Verificar capacidad de bloqueo del archivo (el mismo está listo para ser procesado)
    * Establecer los parámetros de procesamiento en función de:
        - patrones regulares en el nombre
        - patrones regulares dentro del contenido (limite de x bytes)
    * Renombrado de los archivos a punto de procesar en .processing
    * Lectura de los archivos, proceso de las paginas y generación de los reportes oerm
    * Generación de log de proceso. Eventual compresión final del log.
    * Proceso final del Spool. Alguna de estas opciones:
        - Borrado
        - Copiado a otra carpeta
        - Renombrado
        - Compresión en otra carpeta

"""
__author__        = "Patricio Moracho <pmoracho@gmail.com>"
__appname__        = "splwatcher"
__appdesc__        = "Monitor de archivo de spool para conversión a Oerm"
__license__        = 'GPL v3'
__copyright__    = "(c) 2019, %s" % (__author__)
__version__        = "0.9"
__date__        = "2019/05/07"
__config__        = "splwatcher.cfg"

try:
    import gettext
    from gettext import gettext as _
    gettext.textdomain('openerm')

    def my_gettext(s):
        """my_gettext: Traducir algunas cadenas de argparse."""
        current_dict = {'usage: ': 'uso: ',
                        'optional arguments': 'argumentos opcionales',
                        'show this help message and exit': 'mostrar esta ayuda y salir',
                        'positional arguments': 'argumentos posicionales',
                        'the following arguments are required: %s': 'los siguientes argumentos son requeridos: %s'}

        if s in current_dict:
            return current_dict[s]
        return s

    gettext.gettext = my_gettext

    import argparse
    # from argparse import RawTextHelpFormatter
    import sys
    import time
    import os

    sys.path.append('.')
    sys.path.append('..')

    import logging
    from openerm.Config import ProcessorConfig
    from openerm.Config import ConfigLoadingException
    from openerm.Utils import file_accessible
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    from watchdog.events import    PatternMatchingEventHandler
    import psutil

except ImportError as err:
    modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
    print(_("No fue posible importar el modulo: %s") % modulename)
    sys.exit(-1)


def are_same_files(fname1, fname2):
  stat1 = os.stat(fname1)
  stat2 = os.stat(fname2)

  return True if stat1.st_ino == stat2.st_ino and stat1.st_dev == stat2.st_dev else False


def has_handle(fpath):

    for proc in psutil.process_iter():
        try:
            for item in proc.open_files():
                ipath = os.path.abspath(item.path)
                # print(proc.pid,proc.name, "\t", fpath, "\t", ipath)
                if are_same_files(fpath,ipath):
                    return True
        except Exception:
            pass

    return False


class FileReadyChecker():

    def file(self, filepath):
        while has_handle(filepath):
            pass

        print("{0} ready to process".format(filepath))

class Jobs(FileReadyChecker):
    pass

JOBS = Jobs()


class NewSpoolHandler(PatternMatchingEventHandler):
    
    def on_created(self, event):

        filepath = os.path.abspath(event.src_path)

        print("event type: {0} path: {1} {2}".format(    
                                                    event.event_type,
                                                    filepath,
                                                    "En uso" if has_handle(filepath) else ""))

def init_argparse():
    """init_argparse: Inicializar parametros del programa. ``:members:``"""
    cmdparser = argparse.ArgumentParser(prog=__appname__,
                                        description="%s\n%s\n" % (__appdesc__, __copyright__),
                                        epilog="",
                                        add_help=True,
                                        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=66)
    )
    opciones = {    "path": {
                                "type":   str,
                                "action": "store",
                                "help":   _("Path a monitorear")
                    },
                    "--config-file -f": {
                                "type":    str,
                                "action":  "store",
                                "dest":    "configfile",
                                "default": __config__,
                                "help":    _("Archivo de configuración del proceso. Default: {0}").format(__config__)
                    },
                    "--recursive -r": {
                                "action":    "store_true",
                                "dest":    "recursive",
                                "default": False,
                                "help":    _("Proceso recursivo sobre el path a monitorear")
                    }
            }

    for key, val in opciones.items():
        args = key.split()
        kwargs = {}
        kwargs.update(val)
        cmdparser.add_argument(*args, **kwargs)

    return cmdparser


if __name__ == "__main__":

    text = """


███████╗██████╗ ██╗     ██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔══██╗██║     ██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔════╝██╔══██╗
███████╗██████╔╝██║     ██║ █╗ ██║███████║   ██║   ██║     ███████║█████╗  ██████╔╝
╚════██║██╔═══╝ ██║     ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║██╔══╝  ██╔══██╗
███████║██║     ███████╗╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║███████╗██║  ██║
╚══════╝╚═╝     ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

{0} (v.{1})
{2}
"""

    print(text.format(__appdesc__, __version__, __author__))

    cmdparser = init_argparse()
    try:
        args = cmdparser.parse_args()
    except IOError as msg:
        args.error(str(msg))

    # if not args.configfile:
    #    print(_("Error: Debe definir el archivo de configuración del proceso").format(args.configfile))
    #    sys.exit(-1)
    # if not file_accessible(args.configfile, "r"):
    #     print(_("Error: El archivo de configuración del proceso [{0}] no se ha encontrado o no es accesible para su lectura").format(args.configfile))
    #     sys.exit(-1)

    try:
        cfg = ProcessorConfig(args.configfile)

    except FileNotFoundError as e:
        print(_("Error: El archivo de configuración {0} no existe").format(args.configfile))

    except ConfigLoadingException as ex:
        print(_("Error: {0} al leer configuración desde {1}").format(ex.args[0], args.configfile))
        sys.exit(-1)

    else:

        print("Monitoreando {0} {1}".format(args.path, "(Recursivamente)" if args.recursive else ""))
        print("Para finalizar: <Ctrl-C>")

        event_handler = NewSpoolHandler(
                            patterns=None, 
                            ignore_patterns=None, 
                            ignore_directories=True, 
                            case_sensitive=True
                            )


        observer = Observer()
        observer.schedule(event_handler, path=args.path, recursive=args.recursive)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()

        print("")
        sys.exit(-1)

