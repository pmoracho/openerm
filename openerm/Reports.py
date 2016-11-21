# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>

# Reports.py

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
Reports
=======

Clase base para manejar una colección de reportes correspondientes a
un Database OERM.

.. seealso::
	* :class:`openerm.Report`

.. note::
	* Esta clase no debiera usarse directamente
	* En un futuro modificar la inicialización, para que reciba el archivo.oerm y los archivos de los

"""

try:
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')
	import sys

	from openerm.Report import Report

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Reports(object):
	"""Clase base para manejar una colección de reportes correspondientes a
	un Database OERM.

	Args:
		database (:class:`openerm.Database`): Objeto Database

	Returns:
		iterable: Iterador por la lista de Reportes

	Example:
		>>> from openerm.Database import Database
		>>> from openerm.Reports import Reports
		>>> db = Database(file = "out/zstd-level-3-1-22.test.oerm", mode="rb")
		>>> for report in Reports(db):
		...     print(report)
		Report: Reporte 1
		Report: Reporte 2
		>>>

	"""
	def __init__(self, database):

		self.database			= database
		self.current_report		= 0
		self.file				= database._file

	def __len__(self):
		return len(self.database.Index.reports)

	def __iter__(self):
		return self

	def __next__(self):

		self.current_report += 1
		r = self.get_report(self.current_report)
		if not r:
			self.current_report = 0
			raise StopIteration

		return r

	def get_report(self, id):
		"""Retorna un objeto de la clase :class:`openerm.Report` según el **id** del mismo

		Args:
			id (int): Número de reporte de la base Oerm

		Example:
			>>> from openerm.Database import Database
			>>> from openerm.Reports import Reports
			>>> db= Database(file = "out/zstd-level-3-1-22.test.oerm", mode="rb")
			>>> reports = Reports(db)
			>>> reports.get_report(1)
			>>> print(reports.get_report(1))
			Report: Reporte 1

		Return:
			:class:`openerm.Report`: Reporte solicitado

		"""
		if not self.database.Index.reports.get(id):
			return None

		r = Report(self.database, id)

		return r

	def find_text(self, text, search_in_reports=None):
		"""Búsqueda de un texto dentro de uno o más reportes

		Args:
			text (string): Patrón de texto a buscar
			search_in_reports (list): Lista de id´s de reportes dónde buscar o None en todos

		Example:
			>>> from openerm.Database import Database
			>>> from openerm.Reports import Reports
			>>> db = Database(file = "out/.sin_compression_sin_encriptacion.oerm")
			>>> reports = Reports(db)
			>>> reports.find_text("IWY3")
			[(2, 10, 991, 'AGH8B2NULTCTJ0L-[IWY3]-4K6D8RRBYCRQCH')]

		Return:
			Lista de reportes y páginas
				* Reporte id
				* Página
				* Posición en la página
				* Extracto de la ocurrencia a modo de ejemplo
		"""
		matches = []
		if not search_in_reports:
			reports = []
		else:
			reports	= search_in_reports

		for r in [r for r in self if r.id in reports or not reports]:
			lista = r.find_text(text)
			if lista:
				matches.extend(lista)

		return matches
