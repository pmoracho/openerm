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

import unittest

from openerm.SpoolHostReprint import SpoolHostReprint


class SpoolHostReprintTest(unittest.TestCase):

	def test_load_process(self):
		"""Genera un spool y realiza la lectura del mismo
		"""
		paginas = 0
		with SpoolHostReprint(self._filename, 102400) as s:
			for page in s:
				paginas += 1

		self.assertEqual(paginas, 10)

	@classmethod
	def setUpClass(cls):
		cls._filename = "./out/spool.txt"
		cls._generate_spool()

	@classmethod
	def tearDownClass(cls):
		pass

	@classmethod
	def _generate_spool(cls):

		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		with open(cls._filename, "wt") as text_file:
			p = 1
			while p <= 10:
				p += 1
				random_text = rnd_generator(size=200)
				text_file.write("1{0}\n".format(random_text))
				text_file.write(" {0}\n".format(random_text))
