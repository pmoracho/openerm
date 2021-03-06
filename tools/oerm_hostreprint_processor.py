#!python
# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# oerm_hostreprint_processor
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
__author__		= "Patricio Moracho <pmoracho@gmail.com>"
__appname__		= "oerm_hostreprint_processor"
__appdesc__		= "Procesador de archivo de spool (Tipo Host Reprint) a Oerm"
__license__		= 'GPL v3'
__copyright__	= "(c) 2016, %s" % (__author__)
__version__		= "0.9"
__date__		= "2016/07/14"


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
	from openerm.SpoolFixedRecordLength import SpoolFixedRecordLength
	from openerm.Utils import slugify, file_accessible
	from openerm.tabulate import tabulate

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
					"--outputpath -o": {
								"type": str,
								"action": "store",
								"dest": "outputpath",
								"help": _("Path y nombre de achivo oerm final")
					},
					"--version -v": {
								"action":	"version",
								"version":	__version__,
								"help":		_("Mostrar el número de versión y salir")
					},
					"--compressiontype -c": {
								"action":	"store",
								"type":		int,
								"dest":		"compressiontype",
								"default":	1,
								"metavar":	"<tipo>",
								"help":		_("Tipo de compresion a usar. Default: GZIP estándar.")
					},
					"--ciphertype -e": {
								"action":	"store",
								"type":		int,
								"dest":		"ciphertype",
								"metavar":	"<tipo>",
								"default":	0,
								"help":		_("Tipo de encriptación a usar. Default: sin encriptación.")
					},
					"--pagesingroups -p": {
								"action":	"store",
								"type":		int,
								"dest":		"pagesingroups",
								"metavar":	"<cantidad>",
								"default":	10,
								"help":		_("Cantidad de páginas a guardar por contenedor. Por defecto: 10.")
					},
					"--buffersize -b": {
								"action":	"store",
								"type":		int,
								"dest":		"buffersize",
								"metavar":	"<tamaño>",
								"default":	10,
								"help":		_("Cantidad de páginas a guardar por contenedor. Por defecto: 10.")
					},
					"--compression-level -l": {
								"action":	"store",
								"type":		int,
								"dest":		"complevel",
								"metavar":	"<level>",
								"default":	1,
								"help":		_("Nivel de compresión 0=mínimo, 1=normal, 2=máximo. Por defecto: 1.")
					},
					"--testall -t": {
								"action":	"store",
								"type":		str,
								"dest":		"testall",
								"default":	False,
								"help":		_("Verifciación completa. c: algoritmos de compresión, e: algoritmos de encriptación.")
					},
					"--append -a": {
								"action":	"store_true",
								"dest":		"append",
								"default":	False,
								"help":		_("Modo append. Si ya existe el dtabase oerm, agrega el reporte al mismo en vez de truncarlo.")
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


# process_file(filename, args.compressiontype, args.complevel, args.ciphertype,
# args.testall, args.append, args.pagesingroups, args.configfile

def process_file(configfile, inputfile, outputfile,  compressiontype, complevel, ciphertype, testall, append, pagesingroups) :

	block					= Block(default_compress_level=complevel)  # Generic
	resultados				= []
	size_test_file			= os.path.getsize(inputfile)

	compresiones = [e for e in block.compressor.available_types if e[0] == compressiontype]
	encriptados = [e for e in block.cipher.available_types if e[0] == ciphertype]

	if testall:
		if 'e' in testall:
			encriptados = block.cipher.available_types

		if 'c' in testall:
			compresiones = block.compressor.available_types

	mode = "ab" if append else "wb"

	r = ReportMatcher(configfile)
	for encriptado in encriptados:
		for compress in compresiones:

			print("Procesando: {2} Compresión: [{0}] {1} Cifrado: {3}".format(compress[0], compress[1], inputfile, encriptado[1]))

			start		= time.time()
			paginas		= 0

			file_name	= "{0}.{1}.oerm".format(outputfile, slugify("{0}.{1}".format(compress[1], encriptado[1]), "_"))

			db	= Database(	file=file_name,
				 			mode=mode,
							default_compress_method=compress[0],
							default_compress_level=complevel,
				 			default_encription_method=encriptado[0],
							pages_in_container = pagesingroups)

			reportname_anterior = ""

			# spool = SpoolHostReprint(inputfile, buffer_size=102400, encoding="Latin1")
			spool = SpoolFixedRecordLength(inputfile, buffer_size=102400, encoding="cp500", newpage_code="NEVADO" )

			# with SpoolHostReprint(inputfile, buffer_size=102400, encoding="Latin1") as s:
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
			for report in db.reports():
				try:
					for page in report:
						pass
				except Exception as err:
					print("Error: {0} al descomprimir reporte".format(err))
					break

			uncompress_time		= time.time() - start
			container_size 		= compress_size / (db.Index.container_objects + db.Index.metadata_objects)

			resultados.append([
				"[{0}] {1} ({2}p/cont.)".format(compress[0], compress[1], pagesingroups),
				("" if encriptado[0] == 0 else encriptado[1]),
				float(size_test_file),
				float(compress_size),
				(compress_size/size_test_file)*100,
				paginas/compress_time,
				paginas/uncompress_time,
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


def	Main():

	cmdparser = init_argparse()
	try:
		args = cmdparser.parse_args()
	except IOError as msg:
		args.error(str(msg))

	filename = args.inputfile
	if not file_accessible(filename, "rb"):
		print(_("Error: El archivo {0} no se ha encontrado o no es accesible para lectura").format(filename))
		sys.exit(-1)

	if not args.outputpath:
		outputfile = "export"
	else:
		outputfile = args.outputpath

	# if not Utils.file_accessible(outputfile, "wb"):
	# 	print(_("Error: El archivo {0} no es accesible para escritura").format(outputfile))
	# 	sys.exit(-1)

	tablestr = process_file(args.configfile, filename, outputfile,  args.compressiontype, args.complevel, args.ciphertype, args.testall, args.append, args.pagesingroups)

	print("")
	print(tablestr)
	print("")

if __name__ == "__main__":

	Main()

	# import profile
	# import pstats
	# profile.run("Main()", "profile.txt")
	# stats = pstats.Stats('profile.txt')
	# stats.add('profile.txt')
	# # Clean up filenames for the report
	# stats.strip_dirs()
	# # Sort the statistics by the cumulative time spent in the function
	# stats.sort_stats('cumulative')
	# stats.print_stats()
	# print('INCOMING CALLERS:')
	# stats.print_callers()

	# print('OUTGOING CALLEES:')
	# stats.print_callees()
