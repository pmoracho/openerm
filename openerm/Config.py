# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Config.py
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
Config
======

Esta clase gestiona los archivos de configuración del proyecto Oerm. Se encarga
de la carga de los archivos .cfg (formato yaml), realiza la validación de cada
uno y devuelve un diccionario de datos para ser aprovechado luego.

"""

SCHEMA_LOAD = """
load:
	allow_unknown: true
	type: dict
	schema:
		file:
			type: dict
			allow_unknown: true
			schema:
				buffer-size:
					type: integer
					required: true
				encoding:
					type: string
					required: true
				file-type:
					type: string
					required: true
					allowed:
						- fixed
						- fcfc
				record-length:
					type: integer
					required: true
					anyof:
						- {max: 1024,  min: 1}
		output:
			type: dict
			allow_unknown: true
			schema:
				cipher-type:
					required: true
					type: integer
					anyof:
						- {max: 2,	min: 0}
				compress-level:
					required: true
					type: integer
					anyof:
						- {max: 2,	min: 0}
				compress-type:
					required: true
					type: integer
					anyof:
						- {max: 10,  min: 0}
				output-path:
					type: string
					required: true
				file-mask:
					type: string
					required: true
				pages-in-group:
					required: true
					type: integer
					anyof:
						- {max: 10,  min: 1}
		process:
			type: dict
			allow_unknown: true
			schema:
				EOP:
					type: string
					required: true
				report-cfg:
					type: string
					required: true
paths:
	type: dict
"""

try:

	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	import yaml

	sys.path.append('.')
	sys.path.append('..')

	from cerberus import Validator

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class ConfigLoadingException(Exception):
	"""Excepciones especiales para los cargadores de configuraciones"""
	def __init__(self, *args):
		# *args is used to get a list of the parameters passed in
		self.args = [a for a in args]


class Config(object):
	"""
	Clase base para el manejo de configuraciones "jerarquicas".
	Args:
		configfile (string): Nombre del archivo físico de configuración a cargar
		schema (string): Esquema de validación en formato yaml

	Example:
		>>> from openerm.Database import Config
		>>> cfg = Config("file.cfg", schema_yaml)

	"""
	def __init__(self, configfile, schema):

		self.configfile = configfile
		self.schema = schema
		self.dictionary = {}

		self._load_config()

	def _load_config(self):

		with open(self.configfile, 'r', encoding='utf-8') as stream:
			try:
				self.dictionary = yaml.load(stream)
			except yaml.YAMLError as e:
				raise ConfigLoadingException(_("Error de parseo YAML"), [str(e).replace('\n', '')])
			else:
				schema = yaml.load(self.schema.replace("\t", " "))
				v = Validator(schema)
				if not v.validate(self.dictionary):
					errores = []
					for e in v._errors:
						error = "{0}: {1}({2}) Valor: {3}".format("->".join(e.document_path), e.rule, e.constraint, e.value)
						errores.append(error)

					raise ConfigLoadingException(_("Error de validación en el archivo {0}: ").format(self.configfile), errores)

	def _validate_config(self, dictionary, schema_yaml):
		schema = yaml.load(schema_yaml.replace("\t", " "))
		v = Validator(schema)
		return v.validate(dictionary), v._errors


class LoadConfig(Config):
	"""
	Clase base para el manejo de la configuración del proceso de carga.
	"""
	def __init__(self, configfile):

		try:
			super().__init__(configfile, SCHEMA_LOAD)
		except ConfigLoadingException:
			raise
		else:
			for grupo, d in self.dictionary.get("load", {}).items():
				for k, v in d.items():
					setattr(self, k.replace("-", "_"), v)

			self._paths = self.dictionary.get("paths", {})
			self.output_path = self._paths[self.output_path]
