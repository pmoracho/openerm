# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# spool_host_reprint.py
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
Utils
=====

Este módulo contiene todo tipo de funciones de uso general para el
proyecto **OpenErm**

"""

import re
import os
import fnmatch

from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def slugify(text, delim='-'):
	"""Normaliza una cadena para ser usada como nombre de archivo.

	Args:
		text (str): String a normalizar
		delim (str): Caracter de reemplazo de aquellos no válidos

	Ejemplo:
		>>> from openerm.Utils import *
		>>> slugify("Esto, no es válido como nombre de Archivo!", "-")
		'esto-no-es-valido-como-nombre-de-archivo'
	"""
	result = []
	for word in _punct_re.split(text.lower()):
		word = normalize('NFKD', word).encode('ascii', 'ignore')
		word = word.decode('utf-8')
		if word:
			result.append(word)
	return delim.join(result)


def get_values_from_byte(byte):
	"""Retorna dos valores de un byte empaquetado

	Args:
		byte: Entero que represta un byte

	Return
		(v1, v2) Tupla con los dos valores enteros
	"""
	value1 = byte >> 4
	value2 = ((byte << 4) & 255) >> 4
	return value1, value2


def set_byte_from_values(value1, value2):

	"""Retorna un byte empaquetado a partir de dos valores

	Args:
		value1 (int): Entero 0 a 127
		value2 (int): Entero 0 a 127

	Return:
		byte

	"""
	return value1 << 4 | value2


def file_accessible(filepath, mode):
	"""Verifica la accesibilidad de un archivo en un determinado modo de apertura.

	Args:
		filepath (string):
	"""
	try:
		with open(filepath, mode):
			pass
	except IOError:
		return False

	return True


def str_to_list(str, maxvalue):
	"""Devuelve una lista de enteros a partir de un string

	Args:
		str (string): Cadena de números separados por , o -
		maxvalue (int): Máximo valor que puede tener la lista

	Ejemplo:
		>>> from openerm.Utils import *
		>>> str_to_list("1,2,3,4", 10)
		[1, 2, 3, 4]
		>>> str_to_list("1-6,9, 12-14", 15)
		[1, 2, 3, 4, 5, 6, 9, 12, 13, 14]

	"""
	def try_int(s):
		"""Se intenta convertir a un entero sino 0."""
		try:
			return int(s)
		except ValueError:
			return 0

	lista = []
	if str:
		for c in str.split(","):
			if "-" in c:
				rango = c.split("-")
				for valor in range(try_int(rango[0]), try_int(rango[1])+1):
					if 1 <= valor <= maxvalue:
						lista.append(valor)
			else:
				valor = try_int(c)
				if 1 <= valor <= maxvalue:
					lista.append(valor)

	return sorted(lista)


def filesInPath(path, pattern='*.*'):
	"""Retorna de forma recursiva los archivos que respetan un patrón

	Args:
		path (string): Path principal
		pattern (string): (Opcional) patrón a buscar, por defecto '*.*'

	Ejemplo:
		>>> for f in filesInPath("c:\", "*.txt"):
		>>> 	print(f)

	"""
	for dirpath, dirs, filenames in os.walk(path):
		for filename in fnmatch.filter(filenames, pattern):
			relative_path = os.path.relpath(dirpath, path)
			yield os.path.join(relative_path, filename)


class AutoNum():
	"""Clase autonumeradora de valores

	Ejemplo:
		>>> from openerm.Utils import *
		>>> id = AutoNum()
		>>> id.get("Prueba")
		1
		>>> id.get("Otra cosa")
		2
		>>> id.get("Prueba")
		1
	"""

	def __init__(self):
		self.myDict = {}
		self.lastid = 1

	def get(self, value):
		"""Retorna el numerador de un determinado valor

		Args:
			value (any): valor a numerar

		Return:
			int: Número único del valor
		"""
		if not self.myDict.get(value):
			self.myDict[value] 	= self.lastid
			self.lastid			+= 1

		return self.myDict[value]

	def list(self):
		"""Retorna la lista completa de valores, numeradores

		Ejemplo:
			>>> from openerm.Utils import *
			>>> id = AutoNum()
			>>> id.get("Prueba")
			1
			>>> id.get("Otra cosa")
			2
			>>> id.get("Prueba")
			1
			>>> id.list()
			[('Otra cosa', 2), ('Prueba', 1)]

		Return:
			list
		"""
		return list(self.myDict.items())
