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
Software# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import unittest

from openerm.Database import Database


class ReportsTest(unittest.TestCase):


	def test_find_text(self):
		"""Genera un database con info random, y realiza un búsqueda de texto
		"""
		db	= Database(file=self._filename, mode="rb")
		matches = db.find_text("Pagina", [1])
		# print(matches)
		esperado = [(1, 1, 0), (1, 1, 12028), (1, 2, 0), (1, 2, 12028), (1, 3, 0), (1, 3, 12028), (1, 4, 0), (1, 4, 12028), (1, 5, 0), (1, 5, 12028), (1, 6, 0), (1, 6, 12028),
					(1, 7, 0), (1, 7, 12028), (1, 8, 0), (1, 8, 12028), (1, 9, 0), (1, 9, 12028), (1, 10, 0), (1, 10, 12029), (1, 11, 0), (1, 11, 12029), (1, 21, 0), (1, 21, 12028),
					(1, 22, 0), (1, 22, 12028), (1, 23, 0), (1, 23, 12028), (1, 24, 0), (1, 24, 12028), (1, 25, 0), (1, 25, 12028), (1, 26, 0), (1, 26, 12028), (1, 27, 0),
					(1, 27, 12028), (1, 28, 0), (1, 28, 12028), (1, 29, 0), (1, 29, 12028), (1, 30, 0), (1, 30, 12029) ]

		self.assertEqual([(x[0], x[1], x[2]) for x in matches], esperado)

	@classmethod
	def setUpClass(cls):
		cls._filename = "out/test.oerm"
		cls._generate_db(cls._filename, 1, 0)

	@classmethod
	def tearDownClass(cls):
		pass

	@classmethod
	def _generate_db(cls, self, filename, compression, encription=0):

		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		total_pages = 11

		# Primer reporte
		db	= Database(file=self._filename, mode="wb", default_compress_method=compression, default_encription_method=encription, pages_in_container=10)
		db.add_report(reporte="Reporte 1", sistema="Sistema 1", aplicacion="Aplicacion 1", departamento="Departamento 1")
		for i in range(1, total_pages + 1):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			db.add_page(p)
		db.close()

		# Segundo reporte
		db	= Database(file=filename, mode="ab", default_compress_method=compression, default_encription_method=encription, pages_in_container=10)
		# db.add_report( reporte = "Reporte 2", sistema = "Sistema 2", aplicacion = "Aplicacion 2", departamento = "Departamento 2" )
		for i in range(1, total_pages + 1):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			db.add_page(p)
		db.close()
