# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# checkoermdb
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
checkoermdb
===========

Verificación de databases Openermdb

"""

__author__		= "Patricio Moracho <pmoracho@gmail.com>"
__appname__		= "checkoermdb"
__appdesc__		= "Verificador de archivos oerm"
__license__		= 'GPL v3'
__copyright__	= "(c) 2016, %s" % (__author__)
__version__ 	= "0.9"
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

	import sys
	import time
	import os
	import struct
	# import time

	sys.path.append('.')
	sys.path.append('..')

	from openerm.tabulate import tabulate
	from openerm.Block import Block
	from openerm.PageContainer import PageContainer
	from openerm.Utils import file_accessible

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)

class OermDataBase(object):

	def __init__(self, inputfile):

		self.filename		= inputfile
		self.lines			= []
		self.current_line	= 0
		self.current_page	= ""
		self.block			= Block()

	def __enter__(self):

		try:
			self.open_file = open(self.filename, mode="rb")

			struct_fmt	= ">4sB"
			struct_len = struct.calcsize(struct_fmt)
			data = self.open_file.read(struct_len)

			struct_unpack	= struct.Struct(struct_fmt).unpack_from
			magic_number	= struct_unpack(data)[0].decode("utf-8")
			# version			= struct_unpack(data)[1]

			if magic_number != "oerm":
				raise ValueError(_('{0} no es un archivo oerm válido!').format(self.filename))

		except Exception as err:
			print(_("Error al abrir el archivo: {0}").format(err))
			return None

		return self

	def __exit__(self, *args):
		self.open_file.close()
		return True

	def __iter__(self):
		return self

	def __next__(self):

		struct_fmt = '>L'
		struct_len = struct.calcsize(struct_fmt)
		struct_unpack = struct.Struct(struct_fmt).unpack_from

		data = self.open_file.read(struct_len)
		if not data:
			raise StopIteration

		longitud_bloque = struct_unpack(data)[0]

		self.open_file.seek(self.open_file.tell()-struct_len)
		data = self.open_file.read(longitud_bloque)
		if not data:
			raise StopIteration

		return self.block.load(data)


def init_argparse():
	"""init_argparse: Inicializar parametros del programa."""
	cmdparser = argparse.ArgumentParser(prog=__appname__,
										description="%s\n%s\n" % (__appdesc__, __copyright__),
										epilog="",
										add_help=True,
										formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=40)
	)

	cmdparser.add_argument('inputfile'				, type=str,  				action="store"	 						, help="Archivo Excel de entrada")
	cmdparser.add_argument('-v', '--version'     	, action='version', version=__version__								, help='Mostrar el número de versión y salir')
	return cmdparser

if __name__ == "__main__":

	cmdparser = init_argparse()
	try:
		args = cmdparser.parse_args()
	except IOError as msg:
		args.error(str(msg))

	test_file		= args.inputfile

	if not file_accessible(test_file, "rb"):
		print("Error: El archivo {0} no se ha encontrado o no es accesible para lectura".format(test_file))
		sys.exit(-1)

	if test_file:
		size_test_file	= os.path.getsize(test_file)

		resultados = []
		totales = {}
		bloques = 0
		paginas = 0

		start = time.time()
		b = Block()
		pg = PageContainer()
		with OermDataBase(test_file) as bloques:
			for bloque in bloques:

				longitud_bloque, tipo_bloque, tipo_compresion, tipo_encriptacion, longitud_datos, data, variable_data = bloque
				resultados.append([longitud_bloque, tipo_bloque, tipo_compresion, tipo_encriptacion, longitud_datos])
				if tipo_bloque == 2:
					pg.load(data)
					paginas += pg.max_page_count
					k = "{0}. {1} comprimido con {2} (páginas: {3})".format(tipo_bloque, b.block_types[tipo_bloque], b.compressor.available_types[tipo_compresion][1], pg.max_page_count)
				else:
					k = "{0}. {1} comprimido con {2}".format(tipo_bloque, b.block_types[tipo_bloque], b.compressor.available_types[tipo_compresion][1])
				totales[k] = tuple(map(lambda x, y: x + y,  totales.get(k, (0, 0)), (longitud_bloque, 1)))

		elapsed = time.time() - start

		print("")
		print("Archivo          : {0}".format(test_file))
		print("Tamaño en bytes  : {:,.0f}".format(size_test_file))
		print("Total de paginas : {:,.0f}".format(paginas))
		print("Tiempo de lectura: {:,.2f}".format(elapsed))
		print("Tiempo por pag.  : {:,.8f}".format(elapsed/paginas))
		print("Páginas/Segundos : {:,.0f}".format(paginas/elapsed))

		lista = [(v[0], v[1][0], v[1][1], v[1][0]/v[1][1]) for v in totales.items()]
		if lista:
			tablestr = tabulate(
							tabular_data		= lista,
							headers				= ["Tipo bloque", "Tamaño total", "Cantidad", "Bytes promedio por bloque" ],
							floatfmt			= ",.2f",
							tablefmt			= "psql",
							numalign			= "right",
							stralign			= "left",
							override_cols_fmt	= [None, ",.0f", ",.0f", ",.2f"]
			 )
			print("")
			print(tablestr)
			print("")
