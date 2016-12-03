# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# metadata_container
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

import unittest

from openerm.Database import Database
from openerm.Block import Block
from openerm.Utils import slugify


class DatabaseTest(unittest.TestCase):

	def test_generate_and_read_database(self):
		"""Genera un database con info random, lo lee y verifica los resultados
		"""
		block = Block()  # Generic

		for item in block.compressor.available_types:

			filename			= "out/{0}.test.oerm".format(slugify(item[1]))
			paginas_escritas	= self._generate_db(filename, compression=item)

			# Lectura
			paginas_leidas = []
			db	= Database(file=filename, mode="rb")
			for report in db.reports():
				for p in report:
					paginas_leidas.append(p)
			db.close()

			self.assertEqual(paginas_escritas, paginas_leidas)

	def test_find_text(self):
		"""Genera un database con info random, y realiza un búsqueda de texto
		"""
		# def get_nice_string(list_or_iterator):
		# 	return "[" + "\n,".join(str(x) for x in list_or_iterator) + "]"

		block = Block()  # Generic

		for item in block.compressor.available_types:

			filename			= "out/{0}.test.oerm".format(slugify(item[1]))
			# paginas_escritas	= self.__generate_db(filename, compression=item)

			# Lectura

			# paginas_leidas = []
			db	= Database(file=filename, mode="rb")

			matches = db.find_text("Pagina", [1])

			esperado = [(1, 1, 0), (1, 1, 12028), (1, 2, 0), (1, 2, 12028), (1, 3, 0), (1, 3, 12028), (1, 4, 0), (1, 4, 12028), (1, 5, 0), (1, 5, 12028), (1, 6, 0), (1, 6, 12028),
			   			(1, 7, 0), (1, 7, 12028), (1, 8, 0), (1, 8, 12028), (1, 9, 0), (1, 9, 12028), (1, 10, 0), (1, 10, 12029)]

			self.assertEqual([(x[0], x[1], x[2]) for x in matches], esperado)

	@staticmethod
	def _generate_db(filename, compression, encription=0):

		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		total_pages = 11
		paginas_escritas 	= []

		# Primer reporte
		db	= Database(file=filename, mode="wb", default_compress_method=compression[0], default_encription_method=encription, pages_in_container=10)
		db.add_report(reporte="Reporte 1", sistema="Sistema 1", aplicacion="Aplicacion 1", departamento="Departamento 1")
		for i in range(1, total_pages + 1):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			paginas_escritas.append(p)
			db.add_page(p)
		db.close()

		# Segundo reporte
		db	= Database(file=filename, mode="ab", default_compress_method=compression[0], default_encription_method=encription, pages_in_container=10)
		db.add_report(reporte="Reporte 2", sistema="Sistema 2", aplicacion="Aplicacion 2", departamento="Departamento 2")
		for i in range(1, total_pages + 1):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			paginas_escritas.append(p)
			db.add_page(p)
		db.close()

		return paginas_escritas
