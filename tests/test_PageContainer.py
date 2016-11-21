# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# report_pgroup.py
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

import unittest

from openerm.PageContainer import PageContainer


class PageContainerTest(unittest.TestCase):

	def test_add_10_pages_and_test_access(self):
		"""Agrega 10 páginas a un contenedor y prueba el acceso
		"""
		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		paginas = []
		for i in range(1, 11):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			paginas.append(p)

		pgroup = PageContainer(10)
		for p in paginas:
			pgroup.add(p)

		pagedata = pgroup.dump()

		pgroup2 = PageContainer(10)
		pgroup2.load(pagedata)

		for i, p in enumerate(pgroup2, 0):
			self.assertEqual(paginas[i], p)
