# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# test of SpoolHostReprint
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

from openerm.SpoolHostReprint import SpoolHostReprint
from OermTestFixtures import OermTestSpoolFixtures


class SpoolHostReprintTest(OermTestSpoolFixtures):

	def test_load_process(self):
		"""Genera un spool y realiza la lectura del mismo
		"""
		pagina = 0
		read_pages = []
		with SpoolHostReprint(self._spoolfile, 102400) as s:
			for page in s:
				pagina += 1
				read_pages.append(page)

		self.assertEqual(pagina, 10)
		self.assertEqual(self._paginas, read_pages)
