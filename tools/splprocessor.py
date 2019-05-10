# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>

# splprocessor.py

# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
# be included in the file GPL-3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU Library General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

""" 
splprocessor
============

**splprocessor**, es el monitor y procesador de archivos de colas de impresión
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
__author__		= "Patricio Moracho <pmoracho@gmail.com>"
__appname__		= "splprocessor"
__appdesc__		= "Procesador de archivo de spool a Oerm"
__license__		= 'GPL v3'
__copyright__	= "(c) 2019, %s" % (__author__)
__version__		= "0.9"
__date__		= "2019/05/07"

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
	from watchdog.events import LoggingEventHandler
	from watchdog.events import FileSystemEventHandler
	import psutil

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


def has_handle(fpath):

	for proc in psutil.process_iter():
		try:
			for item in proc.open_files():
				ipath = os.path.abspath(item.path)
				print(proc.pid,proc.name, "\t", fpath, "\t", ipath)
				if fpath == ipath:
					return True
		except Exception:
			pass

	return False


class NewSpoolHandler(FileSystemEventHandler):
	
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
										formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)
	)
	opciones = {	"path": {
								"type": str,
								"action": "store",
								"help": _("Path a monitorear")
					},

					"--config-file -f": {
								"type": str,
								"action": "store",
								"dest": "configfile",
								"default":	'splprocessor.cfg',
								"help":		_("Archivo de configuración del proceso.")
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
           _
 ___ _ __ | |_ __  _ __ ___   ___ ___  ___ ___  ___  _ __ 
/ __| '_ \| | '_ \| '__/ _ \ / __/ _ \/ __/ __|/ _ \| '__|
\__ \ |_) | | |_) | | | (_) | (_|  __/\__ \__ \ (_) | |   
|___/ .__/|_| .__/|_|  \___/ \___\___||___/___/\___/|_|   
    |_|     |_|                                           

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
	#	print(_("Error: Debe definir el archivo de configuración del proceso").format(args.configfile))
	#	sys.exit(-1)
	if not file_accessible(args.configfile, "r"):
		print(_("Error: El archivo de configuración del proceso [{0}] no se ha encontrado o no es accesible para su lectura").format(args.configfile))
		sys.exit(-1)

	try:
		cfg = ProcessorConfig(args.configfile)
		# print(cfg.dictionary)

	except ConfigLoadingException as ex:
		pass
		# print(ex.args[0])                                                                                                            
		# print("\n".join([" - " + e for e in ex.args[1]]))

	else:

		print("Monitoreando {0}".format(args.path))
				
		event_handler = NewSpoolHandler()

		observer = Observer()
		observer.schedule(event_handler, path=args.path, recursive=False)
		observer.start()

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			observer.stop()

		observer.join()


		print("")
		sys.exit(-1)
