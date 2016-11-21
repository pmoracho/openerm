#!python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# readoermdb
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""
Readoermdb
==========

"""

__author__		= "Patricio Moracho <pmoracho@gmail.com>"
__appname__		= "readoerdmdb"
__appdesc__		= "Lectura de archivos oerm"
__license__		= 'GPL v3'
__copyright__	= "(c) 2016, %s" % (__author__)
__version__ 	= "0.9"
__date__		= "2016/07/14"


try:
	import sys
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
	import time

	sys.path.append('.')
	sys.path.append('..')

	from openerm.Database import Database
	from openerm.tabulate import *
	from openerm.Utils import *

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
								"help": _("Archivo oerm a leer")
					},
					"--listreports -l": {
								"action":	"store_true",
								"dest":		"listreports",
								"default":	False,
								"help":		_("Listar lor reportes contendios en el archivo Oerm.")
					},
					"--showpages -p": {
								"action":	"store",
								"type":		str,
								"default":	False,
								"dest":		"showpages",
								"metavar":	"<paginas>",
								"help":		_("Mostrar el contenido completo de las páginas indicadas.")
					},
					"--reportid -r": {
								"action":	"store",
								"type":		str,
								"dest":		"reportid",
								"metavar":	"<Id del reporte>",
								"help":		_("Identificador del reporte seleccionado.")
					},
					"--search-text -s": {
								"action":	"store",
								"type":		str,
								"dest":		"searchtext",
								"metavar":	"<texto>",
								"help":		_("Buscar texto en el reporte.")
					}
			}


	for key, val in opciones.items():
		args = key.split()
		kwargs = {}
		kwargs.update(val)
		cmdparser.add_argument(*args, **kwargs)

	return cmdparser

if __name__ == "__main__":

	cmdparser = init_argparse()
	try:
		args = cmdparser.parse_args()
	except IOError as msg:
		args.error(str(msg))

	filename = args.inputfile
	if not file_accessible(filename, "rb"):
		print(_("Error: El archivo {0} no se ha encontrado o no es accesible para lectura").format(filename))
		sys.exit(-1)

	d = Database(filename, mode="rb")

	# Listar reportes en la base oerm
	if args.listreports or (not args.showpages and not args.searchtext):
		reports_list = []
		for report in d.Reports():
			reports_list.append((report.id, report.nombre, report.total_pages))

		if reports_list:
			print("")
			print("Archivo   : {0}".format(filename))
			print("Reportes  : {0}".format(len(reports_list)))
			print("Páginas   : {0}".format(sum([e[2] for e in reports_list])))
			print("")
			tablestr = tabulate(
							tabular_data		= reports_list,
							headers				= ["Reporte", "Nombre", "Páginas" ],
							floatfmt			= ",.2f",
							tablefmt			= "psql",
							numalign			= "right",
							stralign			= "left",
							override_cols_fmt	= [None, None, ",.0f", None]
			 )
			print(tablestr)
			print("")

		d.close()
		sys.exit(0)

	# Consultar un reporte en particular
	if args.reportid:

		report = d.Reports().get_report(int(args.reportid))

		if args.showpages:

			npaginas = str_to_list(args.showpages, report.total_pages)
			if npaginas:
				start = time.time()
				for n in npaginas:
					sys.stdout.buffer.write(report.get_page(n).encode('ascii', "ignore"))

				elapsed = time.time() - start

				print("")
				print("Tiempo de lectura      : {:,.8f} secs.".format(elapsed))
				print("Total de páginas leidas: {:,.0f}".format(len(npaginas)))
				print("Tiempo por página      : {:,.8f} secs.".format(elapsed/len(npaginas)))
				print("")

				d.close()

			sys.exit(0)

		#############################
		# Search a text into a report
		#############################
		if args.searchtext:

			start = time.time()
			matches = report.find_text(args.searchtext)
			elapsed = time.time() - start

			tablestr = tabulate(
							tabular_data		= matches,
							headers				= ["Reporte", "Página", "Posición", "Texto" ],
							floatfmt			= ",.2f",
							tablefmt			= "psql",
							numalign			= "right",
							stralign			= "left",
							override_cols_fmt	= [None, ",.0f", ",.0f", None]
			 )
			print("")
			print("Texto a buscar: {0}".format(args.searchtext))
			print("")
			print(tablestr)
			print("")
			print("Tiempo de lectura      : {:,.8f} secs.".format(elapsed))
			print("Total de ocurrencias   : {:,.0f}".format(len(matches)))
			print("Tiempo por ocurrencia  : {:,.8f} secs.".format(elapsed/len(matches)))
			print("")
			sys.exit(0)
