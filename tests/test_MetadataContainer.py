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
from openerm.MetadataContainer import MetadataContainer


class MetadataContainerTest(unittest.TestCase):

	def test_dump_and_load(self):
		"""Genera un contenedor de metadata con datos random, lo "dumpea" y vuelve a cargar
		"""
		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		data = (rnd_generator(size=50), rnd_generator(size=15), rnd_generator(size=15), rnd_generator(size=15))

		d = MetadataContainer(data[0], data[1], data[2], data[3])
		text = d.dump()

		orig = d.metadata

		o = MetadataContainer()
		o.load(text)

		new = o.metadata
		self.assertTrue(orig == new, "Orig <> new")
