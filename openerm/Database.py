# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Database.py
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
Database
========

Esta clase representa un objeto **Database** de reportes OERM. Basicamente es
el objeto que permite salvar y recuperar reportes electrónicos desde sus
archivos físicos.

.. seealso::
	* :class:`openerm.MetadataContainer`
	* :class:`openerm.PageContainer`

"""

try:
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	import struct
	import datetime

	from openerm.Reports import Reports
	from openerm.Block import Block
	from openerm.PageContainer import PageContainer
	from openerm.MetadataContainer import MetadataContainer
	from openerm.Index import Index
	from openerm.Utils import file_accessible

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Database(object):
	"""Clase base para el manejo de un contenedor de reportes OERM

	Esta clase representa un contenedor de reportes OERM se usa
	para la lectura y escritura de este tipo de datos.

	Args:
		file (string): Nombre del archivo físicos
		mode (string): Modo  'wb', 'ab' o 'rb' (Default: "rb")
		default_compress_method (int): Algoritmo default de compresion
		default_compress_level (int): Nivel de compresión 0=mínimo, 1=normal, 2=máximo. Por defecto: 1.
		default_encription_method (int): Algoritmo de encriptación
		pages_in_container (int): Cantidad de páginas por contenedor

	Example:
		>>> from openerm.Database import Database
		>>> # Apertura en modo lectura
		>>> dbin = Database(file = "out/.sin_compression_sin_encriptacion.oerm")
		>>> # Apertura en modo escritura (NO append)
		>>> dbout = Database(file = "out/.sin_compression_sin_encriptacion.oerm", mode="wb")
	"""
	def __init__(self, file="prueba.oerm",
						mode="rb",
						default_compress_method=1,
						default_compress_level=1,
						default_encription_method=0,
						pages_in_container=10):

		self.default_compress_method	= default_compress_method
		self.default_compress_level		= default_compress_level
		self.default_encription_method	= default_encription_method
		self.pages_in_container			= pages_in_container

		self.flush_pages				= False
		self.current_page				= ""
		self._filename					= file
		self._file						= None
		self.mode						= mode
		self.current_page				= 0

		self.current_report				= 1

		self.block						= Block(default_compress_method=default_compress_method,
												default_compress_level=default_compress_level,
												default_encription_method=default_encription_method
										)
		self.pcontainer					= PageContainer(self.pages_in_container)
		self.Index						= Index(self._filename)
		self.hasflush					= False

		if not file_accessible(self._filename, "r"):
			self.mode = "wb"

		self._open_file()

	def _open_file(self):

		if self.mode == "wb":
			self._file	= open(self._filename, mode=self.mode)
			self._write_magicnumber()
		else:
			if self.mode == "ab":
				self._file	= open(self._filename, mode=self.mode)
				self._file.seek(0, 2)
				self.Index.read()
			else:
				self._file = open(self._filename, mode="rb")
				struct_fmt	= ">4sB"
				struct_len = struct.calcsize(struct_fmt)
				data = self._file.read(struct_len)

				struct_unpack	= struct.Struct(struct_fmt).unpack_from
				magic_number	= struct_unpack(data)[0].decode("Latin1")
				self.version	= struct_unpack(data)[1]

				if magic_number != "oerm":
					raise ValueError(_('{0} no es un archivo oerm válido!').format(self._filename))

				self.Index.read()

	def get_report(self, reporte):
		"""
		Retorna el id de un Reporte
		.. warning::
			Documentación pendiente
		"""
		return self.Index.get_report(reporte)

	def set_report(self, reporte):
		"""
		Establece el reporte actual
		.. warning::
			Documentación pendiente
		"""
		self.current_report = self.Index.get_report(reporte)

	def add_report(self, reporte="n/a", sistema="n/a", aplicacion="n/a", departamento="n/a", fecha=datetime.datetime.now().strftime("%Y%m%d")):
		"""
		Agregar un reporte al contenedor

		.. warning::
			Documentación pendiente

		"""
		if self.hasflush:
			self.flush()

		data	= MetadataContainer(reporte, sistema, aplicacion, departamento, fecha).dump()
		cblock	= self.block.dump(1, data)

		self.current_report = self.Index.add_report(reporte, self._file.tell(), self.pages_in_container)

		self._file.write(cblock)
		self.hasflush = True

	def add_page(self, page):
		"""
		Agregar una página al reporte

		.. warning::
			Documentación pendiente

		"""
		try:
			self.pcontainer.add(page)

		except ValueError:
			self.flush()
			self.pcontainer.add(page)

	def find_text(self, text, reports=None):
		"""Búsqueda de un texto dentro de uno o más reportes

		Args:
			text (string): Patrón de texto a buscar
			reports (list): Lista de reportes dónde buscar o None en todos

		Example:
			>>> from openerm.Database import Database
			>>> db = Database(file = "out/.sin_compression_sin_encriptacion.oerm")
			>>> db.find_text("IWY3")
			[(2, 10, 991, 'AGH8B2NULTCTJ0L-[IWY3]-4K6D8RRBYCRQCH')]

		Return:
			Lista de reportes y páginas
		"""
		reports = reports or []
		matches = []
		for r in [r for r in self.reports() if r.id in reports or not reports]:
			lista = r.find_text(text)
			if lista:
				matches.extend(lista)

		return matches

	def _write_magicnumber(self):

		struct_fmt	= ">4sB"
		data		= struct.pack(struct_fmt, b"oerm", 1)

		self._file.write(data)

	def flush(self):
		"""
		"Comitear" los cambios

		.. warning::
			Documentación pendiente

		"""
		data, var_data	= self.pcontainer.dump()
		cblock			= self.block.dump(2, data, var_data)

		self.Index.add_container(self.current_report, self._file.tell())

		self._file.write(cblock)
		self.pcontainer.clear()

	def close(self):
		"""
		Cerrar el Database

		.. warning::
			Documentación pendiente

		"""
		if self.mode in ["wb", "ab"]:
			self.flush()
			self._file.close()
			self.Index.write()
		else:
			self._file.close()

	def __str__(self):
		s = _("[Database]--->\nArchivo: {0}\nVersion: {0}\n").format(self._file, self.version)
		for i, p in enumerate(self._pages, 1):
			s += "Pagina: {0}:".format(i)
			s += p
		s += "[PageContainer]--->\n"
		return s

	def reports(self):
		"""
		Retorna la colección de Reportes del **Database**

		Return:
			* :class:`openerm.Reports`

		Example:
			>>> from openerm.Database import Database
			>>> db = Database(file = "out/.sin_compression_sin_encriptacion.oerm")
			>>> for report in db.reports():
			...     print(report)
			Report: Reporte 1
			Report: Reporte 2
			>>>

		"""
		# r = Reports(self._file, self.Index.reports)
		r = Reports(self)
		return r
