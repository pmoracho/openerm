# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# spl2oerm
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""
spl2oerm
========

`spl2oerm` es una aplicación de línea de comandos, parte de la familia de
herramientas del proyecto `Openerm <https://github.com/pmoracho/openerm>`_. Este
comando se utiliza para procesar archivos de "spool" (salidas de las colas de
impresión) y realiza las algunas de las siguientes operaciones:

	* Lectura y decodificación del archivo
	* Detección de páginas
	* Detección de reportes
	* Compresión y/o encriptación de páginas
	* Almacenamiento final en Databases "oerm"

Básicamente esta herramienta es un "loader" o "cargador" de los reportes a la
base de datos de un sistema Oerm para su posterior uso y consulta.

Ejecución
=========

Una ejecución sin parámetros muestra esta ayuda::

	uso: spl2oerm [-h] [--config-file CONFIGFILE] inputfile

	Procesador de archivo de spool a Oerm (c) 2016, Patricio Moracho
	<pmoracho@gmail.com>

	argumentos posicionales:
	inputfile                                Archivo a procesar

	argumentos opcionales:
	-h, --help                               mostrar esta ayuda y salir
	--config-file CONFIGFILE, -f CONFIGFILE  Archivo de configuración del proceso.

Esto claramente nos dice, que para ejecutar esta herramienta solo requerimos
dos parámetros:

	* El Archivo "spool" de entrada
	* Un archivo de configuración del proceso que explicaremos a continuación


Configuración del proceso
=========================

El proceso en sí requiere una serie de datos para funcionar y llevar a cabo
exitosamente la carga de los reportes. Esta configuración se define en una
archivo de texto escrito en formato `yaml <http://yaml.org/>`_

Un ejemplo sencillo::

	# vi: ft=yaml
	# Openerm spool file load config file
	#

	load:
		#
		#  Definición del archivo de input
		#
		inputfile:
			encoding: cp500             # Codificación del archivo de entrada
			record-length: 256          # Longitud del registro
			file-type: fixed            # Tipo de input fixed, fcfc
			buffer-size: 102400         # Tamaño del buffer de lectura

		#
		# Definiciones del proceso
		#
		process:
			EOP: NEVADO                 # Caracter o String que define el salto de página
			report-cfg: ./reports.cfg   # Archivo de definición de los reportes

		#
		# Definiciones de la salida
		#
		output:
			output-path: default
			compress-type: 10
			compress-level: 1
			cipher-type: 0
			pages-in-group: 10

Detalle:

	* Toda línea o texto que comienza con el caracter `#` es considerada un comentario
	* La primer sección `load` define completamente el proceso de carga
	* En `file` se configuran los parámetros para la interpretación básica del archivo
		* `encoding` define la codificación del archivo, ver `aqui <https://docs.python.org/3/library/codecs.html#standard-encodings>`_ la lista de psoibles codecs
		* `record-lenght`, para los tipos de archivo de registros de longitud fija, el tamaño de los mismos
		* `file-type` tipo de archivo, actualmente hay dos implementaciones `fixed` y `fcfc`
		* `buffer-size`, tamaño del buffer de lectura, para los archivos de registros de tamño variable.
	* En `process` se configuran los parámetros inherentes al proceso lógico del spool
		* `EOP` define el caracter o cadena que determina el cambio de página dentro del reporte.
		* `report-cfg` define el archivo de configuración de los reportes
	* En `output` se configuran los parámetros que definen el database físico a generar
		* `output-path` define el archivo de configuración de los reportes
		* `compress-type` define el tipo de compresión a usar. Ver más documentación en :class:`openerm.Compressor`
		* `compress-level` define el nivel de compresión a usar. Ver más documentación en :class:`openerm.Compressor`


"""
__author__		= "Patricio Moracho <pmoracho@gmail.com>"
__appname__		= "spl2oerm"
__appdesc__		= "Procesador de archivo de spool a Oerm"
__license__		= 'GPL v3'
__copyright__	= "(c) 2016, %s" % (__author__)
__version__		= "0.9"
__date__		= "2016/11/14"


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

	sys.path.append('.')
	sys.path.append('..')

	from openerm.Config import ConfigLoadingException
	from openerm.LoadProcess import LoadProcess
	from openerm.Utils import file_accessible


except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


def init_argparse():
	"""init_argparse: Inicializar parametros del programa."""
	cmdparser = argparse.ArgumentParser(prog=__appname__,
										description="%s\n%s\n" % (__appdesc__, __copyright__),
										epilog="",
										add_help=True,
										formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)
	)

	opciones = {	"inputfile": {
								"type": str,
								"action": "store",
								"help": _("Archivo a procesar")
					},
					"--config-file -f": {
								"type": str,
								"action": "store",
								"dest": "configfile",
								"default":	None,
								"help":		_("Archivo de configuración del proceso.")
					}
			}

	for key, val in opciones.items():
		args = key.split()
		kwargs = {}
		kwargs.update(val)
		cmdparser.add_argument(*args, **kwargs)

	return cmdparser


def Main():

	cmdparser = init_argparse()
	try:
		args = cmdparser.parse_args()
	except IOError as msg:
		args.error(str(msg))

	filename = args.inputfile
	if not file_accessible(filename, "rb"):
		print(_("Error: El archivo {0} no se ha encontrado o no es accesible para lectura").format(filename))
		sys.exit(-1)

	if not args.configfile:
		print(_("Error: Debe definir el archivo de configuración del proceso").format(args.configfile))
		sys.exit(-1)

	if not file_accessible(args.configfile, "r"):
		print(_("Error: El archivo de configuración del proceso {0} no se ha encontrado o no es accesible para su lectura").format(args.configfile))
		sys.exit(-1)

	try:
		proc = LoadProcess(args.configfile)
	except ConfigLoadingException as ex:
		print(ex.args[0])
		print("\n".join([" - " + e for e in ex.args[1]]))

	else:
		status = proc.process_file(filename)

		print("")
		print(status)
		print("")

if __name__ == "__main__":

	Main()
