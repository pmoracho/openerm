# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# ReportMatcher.py
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
**ReportMatcher** es el objeto que identifica los reportes de una
determinada cola de impresión. Lo hace mediante una serie de reglas que se
definene en una arcchivo de configuración en formato YAML
"""


try:
	import sys
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import yaml
	import datetime

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class ReportMatcher(object):
	"""Matcher de reportes

	Args:
		configfile (string): Path absoluto al archivo de configuración de la clase

	Example:
		>>> from openerm.ReportMatcher import ReportMatcher
		>>> r = ReportMatcher("../var/reports.yaml")
		>>> print(r.match("R8101611"))

	TODO:
	* orden de matching
	* multiples matches x reporte
	"""
	def __init__(self, configfile="openerm.cfg"):

		self.config = {}
		self.reports = {}
		self.matches = []
		self.reports = {}
		self.now = datetime.datetime.now().strftime("%Y%m%d")

		if configfile:
			self.configfile	= configfile
			self.__load_config()
			self._match	= self._match_report
		else:
			self._match	= self._match_none

	def __load_config(self):

		with open(self.configfile, 'r', encoding='utf-8') as stream:
			try:
				self.config = yaml.load(stream)
			except yaml.YAMLError as exc:
				print(exc)

		self.reports = self.config.get("Reports", {})
		for k, rpt in self.reports.items():
			for matches in rpt.get("match", []):
				for match in matches:
					self.matches.append((k, match))


	def match(self, page):
		"""Trata de determinar el reporte en función de los datos de una página

		Args:
			page (string): Texto de la página completa a identificar

		Return:
			tuple: Datos del reporte

		**Datos de retorno**:
			========= ================================================
			Tipo	  Detalle
			========= ================================================
			string	  Id del reporte
			string	  Sistema
			string	  Aplicacion
			string	  Departamento
			string	  Fecha
			========= ================================================


		Example:
			>>> from openerm.ReportMatcher import ReportMatcher
			>>> r = ReportMatcher("../var/reports.yaml")
			>>> print(r.match("R8101611"))
		"""
		return self._match(page)

	@staticmethod
	def _match_none(page):
		return ("Sin Identificar", "n/a", "n/a", "n/a", "n/a")

	def _match_report(self, page):

		for k, match in self.matches:
			if match in page:
				d = (	k,
						self.reports[k].get("system", "n/a"),
						self.reports[k].get("application", "n/a"),
						self.reports[k].get("department", "n/a"),
						self.reports[k].get("date", self.now)
					)
				return d

		return ("Sin Identificar", "n/a", "n/a", "n/a", "n/a")


if __name__ == "__main__":
	r = ReportMatcher("../var/reports.yaml")
	print(r.match("R8101611"))
