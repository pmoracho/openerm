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
Report
======

Este objeto representa un Reporte almacenado en un :class:`openerm.Database`.

Ejemplo:

Un reporte por su parte posee:

	* Páginas
	* Metadatos o atributos

.. seealso::
	* :class:`openerm.Reports`
	* :class:`openerm.Database`

"""

try:
	import sys
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import struct
	from openerm.Block import Block
	from openerm.PageContainer import PageContainer
	from openerm.MetadataContainer import MetadataContainer

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Report(object):
	"""Clase para el manejo de un Reporte OERM.

	Args:
		database: Objeto :class:`openerm.Database`
		idrpt (int): Identificador único del reporte en el Database

	Example:
		>>> fuerom openerm.Database import Database
		>>> from openerm.Report import Report
		>>> db = Database(file = "out/zstd-level-3-1-22.test.oerm", mode="rb")
		>>> r = Report(db, 1)
		>>> for page in r:
		...     print(page[0:10])
		...
		Pagina 1 -
		Pagina 2 -
		Pagina 3 -
		Pagina 4 -
		Pagina 5 -
		Pagina 6 -
		Pagina 7 -
		Pagina 8 -
		Pagina 9 -
		Pagina 10
		Pagina 11

	**data**:
		========= ================================================
		Tipo	  Detalle
		========= ================================================
		int       Id del reporte
		string    Nombre del reporte
		long      Offset al contenedor de metadatos
		long      Max cantidad de páginas en los PageContainers
		long      Offset al primer PageContainer
		list      Lista de Offsets a los PageContainers
		========= ================================================

	"""
	# def __init__(self, file, data):
	def __init__(self, database, idrpt):

		data 						= (idrpt,) + database.Index.reports[idrpt]

		self.file					= database._file
		self.id 					= data[0]							#: id del reporte
		self.nombre 				= data[1]							#: Nombre del reporte
		self.metadata_offset 		= data[2]
		self.max_pages_in_container = data[3]
		self.first_p_container 		= data[4]
		self.containers_offset		= data[5]
		self.total_containers		= len(self.containers_offset)
		self.current_page			= 1
		self.current_container		= -1
		self.current_block_data		= None
		self.block					= Block()
		self.pagecontainer 			= PageContainer()
		self.metadatacontainer		= MetadataContainer()
		self.metadata				= {}								#: Metadatos del reporte
		self.total_pages			= 0									#: Cantidad total de páginas del reporte

		self._get_report_data()

	def _get_block_data_from_container(self, container):

		container_offset = self.containers_offset[container]
		return self._get_block_data_from_offset(container_offset)

	def __len__(self):
		return self.total_pages

	def __iter__(self):
		return self

	def __next__(self):
		p = self.get_page(self.current_page)
		if not p:
			self.current_page = 1
			raise StopIteration
		else:
			self.current_page += 1
		return p

	def __str__(self):
		return "Report: {0} ".format(self.nombre)

	def get_page(self, pagenum):
		"""Retorna una pagina del reporte

		Args:
			pagenum(int): Número de página

		Example:
			>>> from openerm.Database import Database
			>>> from openerm.Report import Report
			>>> db = Database(file = "out/zstd-level-3-1-22.test.oerm", mode="rb")
			>>> r = Report(db, 1)
			>>> p = r.get_page(5)
			>>> print(p[0:30])
			Pagina 5 -----------------
			ZSV
			>>>

		Return:
			string: Texto completo de la página

		"""
		container = int((pagenum - 1) / self.max_pages_in_container)
		if container > self.total_containers - 1:
			return None

		if container != self.current_container:
			self.current_block_data = self._get_block_data_from_container(container)
			# (longitud_bloque, tipo_bloque, tipo_compresion, tipo_encriptacion, longitud_datos, data, variable_data)
			self.pagecontainer.load((self.current_block_data[5], self.current_block_data[6]))
			self.current_container = container

		relative_pagenum = pagenum - (container * self.max_pages_in_container)

		return self.pagecontainer.get_page(relative_pagenum)

	def _get_report_data(self):

		# La cantidad de contenedores - 1 por la cantidad de paginas x contenedor da el primer número
		last_container_offset = self.total_containers - 1
		total = (self.total_containers - 1) * self.max_pages_in_container
		# Leer el último contenedor para saber cuantas páginas quedaron en él
		data = self._get_block_data_from_container(last_container_offset)
		self.pagecontainer.load((data[5], data[6]))
		total += len(self.pagecontainer)

		self.total_pages = total

		# Metadatos
		longitud_bloque, tipo_bloque, tipo_compresion, tipo_encriptacion, longitud_datos, data, variable_data = self._get_block_data_from_offset(self.metadata_offset)
		self.metadata = self.metadatacontainer.load(data)
		self.__dict__.update(self.metadata)

	def _get_block_data_from_offset(self, container_offset):

		self.file.seek(container_offset)

		struct_fmt = '>L'
		struct_len = struct.calcsize(struct_fmt)
		struct_unpack = struct.Struct(struct_fmt).unpack_from

		data = self.file.read(struct_len)
		if not data:
			return None

		longitud_bloque = struct_unpack(data)[0]

		self.file.seek(self.file.tell() - struct_len)
		data = self.file.read(longitud_bloque)
		if not data:
			return None

		# (longitud_bloque, tipo_bloque, tipo_compresion, tipo_encriptacion, longitud_datos, data, variable_data)
		return self.block.load(data)

	def find_text(self, text):
		"""Búsqueda de un texto dentro del reporte

		Args:
			text (string): Patrón de texto a buscar

		Example:
			>>> from openerm.Database import Database
			>>> from openerm.Report import Report
			>>> db = Database(file = "out/.sin_compression_sin_encriptacion.oerm")
			>>> r = Report(db, 1)
			>>> report.find_text("IWY3")
			[(2, 10, 991, 'AGH8B2NULTCTJ0L-[IWY3]-4K6D8RRBYCRQCH')]

		Return:
			Lista de reportes y páginas
				* Reporte id
				* Página
				* Posición en la página
				* Extracto de la ocurrencia a modo de ejemplo
		"""
		def sample(find, text, pos, lfind):

			start 	= pos - 15
			end 	= pos + lfind + 15

			if start < 0:
				start = 0

			if end > len(text):
				end = len(text)

			return text[start:pos] + "-[" + find + "]-" + text[pos + lfind + 1:end]

		lfind 	= len(text)
		ocurrences 	= []
		for np in range(1, self.total_pages):
			p = self.get_page(np)
			if p:
				pos = p.find(text)
				while pos >= 0:
					sampletext = sample(text, p, pos, lfind)
					ocurrences.append((self.id, np, pos, sampletext.replace("\n", "")))
					pos = p.find(text, pos + 1)

		return ocurrences
