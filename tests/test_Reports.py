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

from openerm.Database import Database
from openerm.Block import Block
from OermTestFixtures import OermTestCatalogFixtures
import os


class ReportsTest(OermTestCatalogFixtures):

	def test_reports_find_text(self):
		"""Genera un database con info random, y realiza un búsqueda de texto
		"""
		block = Block()  # Generic

		for item in block.compressor.available_types:

			filename = os.path.join(self._repopath, "test.{0}-{1}.oerm".format(item[0], 0))
			db = Database(file=filename, mode="rb")

			matches = db.reports().find_text(text="Pagina", search_in_reports=[2])
			# print(matches)
			esperado = [(2, 1, 0), (2, 1, 12029), (2, 2, 0), (2, 2, 12029), (2, 3, 0), (2, 3, 12029), (2, 4, 0), (2, 4, 12029), (2, 5, 0), (2, 5, 12029), (2, 6, 0), (2, 6, 12029),
					(2, 7, 0), (2, 7, 12029), (2, 8, 0), (2, 8, 12029), (2, 9, 0), (2, 9, 12029), (2, 10, 0), (2, 10, 12029)]

			self.assertEqual([(x[0], x[1], x[2]) for x in matches], esperado)
