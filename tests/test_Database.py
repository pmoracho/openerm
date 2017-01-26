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

import os

from openerm.Database import Database
from openerm.Block import Block
from OermTestFixtures import OermTestFixtures


class DatabaseTest(OermTestFixtures):

	def test_read_database(self):
		"""Lee un database con info random y verifica los resultados"""
		block = Block()  # Generic

		for item in block.compressor.available_types:

			filename       = os.path.join(self._repopath, "test.{0}-{1}.oerm".format(item[0], 0))
			paginas_leidas = []
			db             = Database(file=filename, mode="rb")
			for report in db.reports():
				for p in report:
					paginas_leidas.append(p)
			db.close()
			self.assertEqual(self._paginas_escritas, paginas_leidas)

	def test_find_text(self):
		"""Genera un database con info random, y realiza un búsqueda de texto"""
		block = Block()  # Generic

		for item in block.compressor.available_types:

			filename = os.path.join(self._repopath, "test.{0}-{1}.oerm".format(item[0], 0))
			db       = Database(file=filename, mode="rb")
			matches  = db.find_text("Pagina", reports=[1])
			esperado = [(1, 1, 0), (1, 1, 12028), (1, 2, 0), (1, 2, 12028), (1, 3, 0), (1, 3, 12028), (1, 4, 0), (1, 4, 12028), (1, 5, 0), (1, 5, 12028), (1, 6, 0), (1, 6, 12028),
			   			(1, 7, 0), (1, 7, 12028), (1, 8, 0), (1, 8, 12028), (1, 9, 0), (1, 9, 12028), (1, 10, 0), (1, 10, 12028)]

			self.assertEqual([(x[0], x[1], x[2]) for x in matches], esperado)
