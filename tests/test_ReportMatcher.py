# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# test_ReportMatcher
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

import sys
sys.path.append('.')
sys.path.append('..')

import unittest
from openerm.ReportMatcher import ReportMatcher

class ReportMatcherTest(unittest.TestCase):

	test_page = """
	1. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus non lectus scelerisque, accumsan turpis at, malesuada
	2. turpis. Quisque in orci consectetur, hendrerit risus in, laoreet tortor. Ut tempor, diam in iaculis ullamcorper, libero
	3. orci consequat tortor, non lacinia lorem ipsum id nisi. Duis condimentum, lacus nec lobortis tristique, sapien massa
	4. accumsan nisl, non finibus massa metus eu risus. Vestibulum placerat augue orci, et mattis neque fermentum suscipit.
	5. Fusce a sem tincidunt, vehicula tellus sed, pretium massa. Fusce ante diam, vestibulum eu nulla eu, pulvinar aliquet
	6. felis. Praesent tristique ligula eget leo sollicitudin, a dapibus mauris cursus. Praesent maximus nibh ut venenatis
	7. blandit.
	8.       1         2         3         4
	1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
	10. Suspendisse potenti. Phasellus interdum massa sed eros auctor ornare. Morbi eget eros aliquam, aliquam tortor nec,
	11. interdum augue. Sed auctor ex vel libero rhoncus, sed malesuada diam sodales. Vestibulum sollicitudin ac nisi non viverra.
	12. Duis pharetra massa nec nisi varius facilisis. Quisque sed scelerisque metus. Ut auctor condimentum libero sit amet
	13. dapibus. Vestibulum sed sem lobortis, vulputate nunc sed, ultricies felis. Phasellus dictum porta libero eu pellentesque.
	143. Sed placerat et lorem vitae ultrices. In semper nec velit et ultricies.
	"""

	def test_simple_match(self):
		"""Pruebas de un matching simple de reporte, se busca en todo el texto"""


		config = """
		Reports:
			"Prueba":
				match:
					"Lorem ipsum dolor sit amet":

				system: "Sistema"
				application: "Aplicacion"
				department: "Departamento"

		"""
		r = ReportMatcher(configbuffer=config)

		self.assertEqual(r.match(self.test_page)[0], "Prueba")

	def test_box_match(self):
		"""Pruebas de un matching único con recorte por box"""


		config = """
		Reports:
			"Prueba":
				match:
					"Phasellus interdum": [6, 11, 20, 45]

				system: "Sistema"
				application: "Aplicacion"
				department: "Departamento"

		"""
		r = ReportMatcher(configbuffer=config)

		self.assertEqual(r.match(self.test_page)[0], "Prueba")
