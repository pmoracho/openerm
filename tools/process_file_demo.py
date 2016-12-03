# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# process_file_demo.py
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

try:
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys

	from Database import Database
	from SpoolHostReprint import SpoolHostReprint

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


if __name__ == "__main__":

	import time
	import os
	from Block import Block
	from tabulate import tabulate

	resultados = []
	encriptado = 0

	block = Block() # Generic

	test_file		= "d:/mfw/test.txt"
	size_test_file 	= os.path.getsize(test_file)

	for item in block.compressor.available_types:

		print("Procesando: [{0}] {1}".format(item[0],item[1]))

		start = time.time()
		paginas = 0

		file_name		= "out\{0}.prueba.oerm".format(item[1])

		db	= Database(file = file_name, default_compress_method=item[0], default_encription_method=0, pages_in_container = 10)

		db.add_report( reporte = "Sin identificar", sistema = "n/a", aplicacion = "n/a", departamento = "n/a" )

		with SpoolHostReprint(test_file, buffer_size=102400, encoding="Latin1") as s:
			for page in s:
				paginas = paginas + 1
				db.add_page(page)

		db.close()

		compress_time 	= time.time() - start
		compress_size	= os.path.getsize(file_name)

		start = time.time()
		db	= Database(file = file_name, mode="rb")
		for report in db.reports():
			for page in report:
				pass
		uncompress_time 	= time.time() - start

		resultados.append( [
			"[{0}] {1}".format(item[0],item[1]),
			("" if encriptado == 0 else "Si"),
			size_test_file,
			compress_size,
			(compress_size/size_test_file)*100,
			compress_time,
			paginas/compress_time,
			uncompress_time,
			paginas/uncompress_time
		])


	tablestr = tabulate(
					tabular_data		= resultados,
					headers				= ["Algoritmo", "Encriptado", "Real (bytes)", "Comprimido (bytes)", "Ratio", "Compr. seg.", "Pag/Seg", "Descompr. seg.", "Pag/Seg" ],
					floatfmt			= "8.2f",
					tablefmt			= "psql",
					numalign			= "right",
					stralign			= "left"
	 )
	print("")
	print(tablestr)
	print("")


