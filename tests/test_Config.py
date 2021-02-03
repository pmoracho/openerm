# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# test of Config class
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
import yaml
from openerm.Config import Config, ConfigLoadingException


class ConfigTest(unittest.TestCase):

	data = { "A": 'a',
		 	 "D": {
					"C": 'c',
					"D": 'd',
					"E": 'e'
				},
		 	"L": [1,2,3,4,5]
		 }
	schema = """
	A:
		type: string
	D:
		type: dict
		allow_unknown: true
		schema:
			C:
				type: string
				required: true
				allowed:
						- x
						- z
			D:
				type: string
			E:
				type: integer
				required: true
	L:
		type: list
	"""

	def test_generate_yaml_and_load(self):
		"""Genera un archivo yaml y realiza la importación en un diccionario
		"""
		cfg = Config(self._filename)
		self.assertEqual(cfg.dictionary, self.data)

		errores_esperados = ["D: schema({'C': {'type': 'string', 'required': True, 'allowed': ['x', 'z']}, 'D': {'type': 'string'}, 'E': {'type': 'integer', 'required': True}}) Valor: {'C': 'c', 'D': 'd', 'E': 'e'}"]
		try:
			cfg = Config(self._filename,self.schema)
		except ConfigLoadingException as ex:
			lista = [e for e in ex.args[1]]
			self.assertEqual(lista, errores_esperados)

	@classmethod
	def setUpClass(cls):
		cls._filename = "./out/test.yaml"
		cls._generate_yaml()

	@classmethod
	def tearDownClass(cls):
		pass

	@classmethod
	def _generate_yaml(cls):

		with open(cls._filename, 'w') as outfile:
			yaml.dump(cls.data, outfile, default_flow_style=True)
