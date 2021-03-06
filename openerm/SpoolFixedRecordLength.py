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
Un **SpoolFixedRecordLength** es el objeto que permite la lectura de las salidas
de impresión del tipo Registro de longitud fija. Este formato es típico en
plataformas IBM, archivos en EBCDIC con una longitud de registro de 256 bytes
son habituales de ver. Cada registro representa una línea, puede eventualmente
ser del tipo FCFC, y contar con un canal de control.


.. seealso::
	* :class:`openerm.SpoolHostReprint`
"""


class SpoolFixedRecordLength(object):
	"""Clase base para lectura de archivos de tamaño de registro fijo.

	Args:
		inputfile (string): Path y nombre del archivo a leer
		buffer_size (int): 	Opcional, tamaño del buffer de lectura.
							Por defecto 102400 bytes.
		encoding (string): 	Opcional, Codificación de lectura. Por defecto `Latin1`
		record_len (int): 	Opcional, Longitud de registro (por defecto 256)
		newpage_code (string):
							Opcional, Cadena o carácter que determina el salto de página

	Return:
		None

	:Ejemplo:
		>>> from openerm.SpoolFixedRecordLength import SpoolFixedRecordLength
		>>> with SpoolFixedRecordLength(test_file, 102400) as s:
		>>>		for page in s:
		>>>			print(page)

	"""
	def __init__(self, inputfile, buffer_size=102400, encoding="Latin1", record_len=256, newpage_code="1"):

		self.filename		= inputfile
		self.buffer_size	= buffer_size
		self.encoding		= encoding
		self.record_len		= record_len
		self.newpage_code	= newpage_code
		self.lnewpage_code	= len(newpage_code)

		self._current_line	= 0
		self._current_page	= ""
		self._last_chunk	= False

		self._lines			= []
		self._newpage		= False

	def __enter__(self):
		"Apertura del archivo del spool a procesar"
		# file_size		= os.path.getsize(self.filename)
		self.open_file 	= open(self.filename, mode="r", encoding=self.encoding)
		return self

	def __exit__(self, *args):
		"Cierre automatico del spool"
		self.open_file.close()
		return True

	def __iter__(self):
		return self

	def __next__(self):
		"""Devuelve una página del spool"""

		if self._current_page is None:
			raise StopIteration

		while True:
			line = self.open_file.read(self.record_len)
			if not line:
				# Fin de archivo
				page = self._current_page
				self._current_page = None
				return page

			line = line.rstrip() + "\n"
			if line[0:self.lnewpage_code] == self.newpage_code and self._current_page != "":
				# Detectado fin de página
				page = self._current_page
				self._current_page = line
				return page
			else:
				self._current_page += line
