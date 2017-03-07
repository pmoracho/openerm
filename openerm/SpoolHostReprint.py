# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>

# SpoolHostReprint.py

# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation. A copy of this license should
# be included in the file GPL-3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU Library General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""
Un **SpoolHostReprint** es el objeto que permite la lectura de las salidas de
impresión del tipo FCFC que son aquellos en los que la primer columna
representa un "canal" de control para la impresora. Esta clase considera esta
columna  y particularmente el codigo "1" que representa el salto de pagina.
Esta columna podra ser quitada o no segun se requiera.

.. seealso::
	* :class:`openerm.SpoolFixedRecordLength`

"""


class SpoolHostReprint(object):
	"""Clase base para lectura de archivos tipo "host reprint".

	Args:
		inputfile (string): Path y nombre del archivo a leer
		buffer_size (int): 	Opcional, tamaño del buffer de lectura.
							Por defecto 102400 bytes.
		encoding (string): 	Opcional, Codificación de lectura. Por defecto `Latin1`

	Return:
		None

	:Example:
		>>> from openerm.SpoolHostReprint import SpoolHostReprint
		>>> with SpoolHostReprint(test_file, 102400) as s:
		>>>		for page in s:
		>>>			print(page)

	"""
	def __init__(self, inputfile, buffer_size=102400, encoding="Latin1"):

		self.filename		= inputfile
		self.buffer_size	= buffer_size
		self.encoding		= encoding

		self._current_line	= 0
		self._current_page	= ""
		self._last_chunk	= False

		self._lines			= []

	def __enter__(self):
		"Apertura del archivo del spool a procesar"
		self.open_file = open(self.filename, mode="rt", encoding=self.encoding)
		return self

	def __exit__(self, *args):
		"Cierre automatico del spool"
		self.open_file.close()
		return True

	def __iter__(self):
		return self

	def __next__(self):
		"""Devuelve la siguiente página leída

		Return:
			string: Texto completo de la página

		"""

		if self._current_line >= len(self._lines):
			self._lines = self.open_file.readlines(self.buffer_size)
			if not self._lines:
				if self._current_page == "":
					raise StopIteration
				else:
					page = self._current_page
					self._current_page = ""
					return page

			self._current_line = 0

		for line in self._lines[self._current_line:]:
			self._current_line += 1
			if line[0] == "1" and self._current_page != "":
				page = self._current_page
				#s elf._current_page =  line[1:] # <- Se quita la pimer columna de comandos
				self._current_page = line
				return page

			# self._current_page = self._current_page + line[1:] # <- Se quita la pimer columna de comandos
			self._current_page += line

		return self.__next__()
