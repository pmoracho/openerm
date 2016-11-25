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
		file:
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
	import time
	import os

	sys.path.append('.')
	sys.path.append('..')

	from openerm.Block import Block
	from openerm.Database import Database
	from openerm.ReportMatcher import ReportMatcher
	from openerm.SpoolHostReprint import SpoolHostReprint
	from openerm.SpoolFixedRecordLenght import SpoolFixedRecordLenght
	from openerm.Utils import slugify, file_accessible
	from openerm.tabulate import tabulate
	from openerm.Config import LoadConfig
	from openerm.Config import ConfigLoadingException

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class LoadProcess(object):

	def __init__(self, configfile):

		self.config = LoadConfig(configfile)

	def process_file(self, inputfile):

		block					= Block(default_compress_level=self.config.compress_level)
		resultados				= []
		size_test_file			= os.path.getsize(inputfile)

		compresiones = [e for e in block.compressor.available_types if e[0] == self.config.compress_type]
		encriptados = [e for e in block.cipher.available_types if e[0] == self.config.cipher_type]

		mode = "ab"

		r = ReportMatcher(self.config.report_cfg)

		for encriptado in encriptados:
			for compress in compresiones:

				print("Procesando: {2} Compresión: [{0}] {1} Cifrado: {3}".format(compress[0], compress[1], inputfile, encriptado[1]))

				start		= time.time()
				paginas		= 0

				# file_name	= "{0}.{1}.oerm".format(self.config.output_path, slugify("{0}.{1}".format(compress[1], encriptado[1]), "_"))
				file_name	= os.path.join(self.config.output_path, self.config.file_mask + ".oerm" )

				db	= Database(	file=file_name,
								mode=mode,
								default_compress_method=compress[0],
								default_compress_level=self.config.compress_level,
								default_encription_method=encriptado[0],
								pages_in_container = self.config.pages_in_group)

				reportname_anterior = ""

				sppol_types = { "fixed": SpoolFixedRecordLenght(inputfile, buffer_size=self.config.buffer_size, encoding=self.config.encoding, newpage_code=self.config.EOP ),
				   				"fcfc":	SpoolHostReprint(inputfile, buffer_size=self.config.buffer_size, encoding=self.config.encoding )
				}

				spool = sppol_types[self.config.file_type]
				with spool as s:
					for page in s:
						data = r.match(page)
						reportname = data[0]
						if reportname != reportname_anterior:
							db.add_report(reporte=reportname, sistema=data[1], aplicacion=data[2], departamento=data[3], fecha=data[4])
							reportname_anterior = reportname

						paginas = paginas + 1
						db.add_page(page)

				db.close()

				compress_time	= time.time() - start
				compress_size	= os.path.getsize(file_name)

				start = time.time()
				db	= Database(file=file_name, mode="rb")
				for report in db.Reports():
					try:
						for page in report:
							pass
					except Exception as err:
						print("Error: {0} al descomprimir reporte".format(err))
						break

				uncompress_time		= time.time() - start
				container_size 		= compress_size / (db.Index.container_objects + db.Index.metadata_objects)

				resultados.append([
					"[{0}] {1} ({2}p/cont.)".format(compress[0], compress[1], self.config.pages_in_group),
					("" if encriptado[0] == 0 else encriptado[1]),
					float(size_test_file),
					float(compress_size),
					(compress_size/size_test_file)*100,
					paginas/compress_time,
					paginas/uncompress_time if uncompress_time else paginas,
					container_size
				])


		tablestr = tabulate(
						tabular_data		= resultados,
						headers				= ["Algoritmo", "Encript.", "Real (bytes)", "Compr. (bytes)", "Ratio", "Compr. Pg/Seg", "Descompr. Pg/Seg", "BSize (Prom.)" ],
						floatfmt			= "8.2f",
						tablefmt			= "psql",
						numalign			= "right",
						stralign			= "left",
						override_cols_fmt	= [None, None, ",.0f", ",.0f",",.2f", ",.2f", ",.2f", ",.2f", ",.2f" ]
		)
		return tablestr


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

	try:
		proc = LoadProcess(args.configfile)
	except ConfigLoadingException as ex:
		print(ex.args[0])
		print("\n".join([" - " + e for e in ex.args[1]]))

	else:
		tablestr = proc.process_file(filename)

		print("")
		print(tablestr)
		print("")

if __name__ == "__main__":

	Main()
