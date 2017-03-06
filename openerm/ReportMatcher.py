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
		configbuffer (string): Buffer con la configuración YAML de la clase.
		Este parámatro tiene prioridad en caso de ingresar tambien configfile

	Example:
		>>> from openerm.ReportMatcher import ReportMatcher
		>>> r = ReportMatcher("../var/reports.yaml")
		>>> print(r.match("R8101611"))

	TODO:
	* orden de matching
	* multiples matches x reporte
	"""
	def __init__(self, configfile="openerm.cfg", configbuffer=None):

		self.config  = {}
		self.reports = {}
		self.matches = []
		self.reports = {}
		self.now     = datetime.datetime.now().strftime("%Y%m%d")

		if configbuffer:
			self.config = yaml.load(configbuffer.replace("\t", " "))
		elif configfile:
			self.configfile	= configfile
			self.__load_config_file()
			self._match	= self._match_report
		else:
			self._match	= self._match_none

		self.reports = self.config.get("Reports", {})
		for k, rpt in self.reports.items():
			matches = rpt.get("match", {})
			for match, box in matches.items():
				self.matches.append((k, match, box))


	def __load_config_file(self):

		with open(self.configfile, 'r', encoding='utf-8') as stream:
			try:
				self.config = yaml.load(stream)
			except yaml.YAMLError as exc:
				print(exc)

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
		return self._match_report(page)

	@staticmethod
	def _match_none(page):
		return ("Sin Identificar", "n/a", "n/a", "n/a", "n/a")

	def _match_report(self, text):

		for reporte, match, box in self.matches:

			if box:
				for i,l in enumerate(text.split("\n"),1):
					if i in range(box[0], box[1]+1):
						print(l[box[2]-1:box[3]+1])
						if match in l[box[2]-1:box[3]+1]:
							d = (	reporte,
									self.reports[reporte].get("system", "n/a"),
									self.reports[reporte].get("application", "n/a"),
									self.reports[reporte].get("department", "n/a"),
									self.reports[reporte].get("date", self.now)
								)
							return d
			else:

				if match in text:
					d = (	reporte,
							self.reports[reporte].get("system", "n/a"),
							self.reports[reporte].get("application", "n/a"),
							self.reports[reporte].get("department", "n/a"),
							self.reports[reporte].get("date", self.now)
						)
					return d

		return ("Sin Identificar", "n/a", "n/a", "n/a", "n/a")


def test():
	conf = """
	Reports:
		L80010 - CLIENTES - PERSONA JURIDICA:
			match:
				L80010: [1, 1, 2, 10]
				L80011:
			system: "Sistema"
			application: "Aplicacion"
			department: "Departamento"
	"""
	test_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus non lectus scelerisque, accumsan turpis at, malesuada
	L80010, turpis. Quisque in orci consectetur, L80010 hendrerit risus in, laoreet tortor. Ut tempor, diam in iaculis ullamcorper, libero
	orci consequat tortor, non lacinia lorem ipsum id nisi. Duis condimentum, lacus nec lobortis tristique, sapien massa
	accumsan nisl, non finibus massa metus eu risus. Vestibulum placerat augue orci, et mattis neque fermentum suscipit.
	Fusce a sem tincidunt, vehicula tellus sed, pretium massa. Fusce ante diam, vestibulum eu nulla eu, pulvinar aliquet
	felis. Praesent tristique ligula eget leo sollicitudin, a dapibus mauris cursus. Praesent maximus nibh ut venenatis
	blandit.

	Suspendisse potenti. Phasellus interdum massa sed eros auctor ornare. Morbi eget eros aliquam, aliquam tortor nec,
	interdum augue. Sed auctor ex vel libero rhoncus, sed malesuada diam sodales. Vestibulum sollicitudin ac nisi non viverra.
	Duis pharetra massa nec nisi varius facilisis. Quisque sed scelerisque metus. Ut auctor condimentum libero sit amet
	dapibus. Vestibulum sed sem lobortis, vulputate nunc sed, ultricies felis. Phasellus dictum porta libero eu pellentesque.
	Sed placerat et lorem vitae ultrices. In semper nec velit et ultricies.
	"""

	# r = ReportMatcher("../var/reports.yaml")
	r = ReportMatcher(configbuffer=conf)
	print(r.match(test_text*100))

if __name__ == "__main__":
	# import timeit
	# setup = "from __main__ import test"
	# print(timeit.timeit("test()", setup=setup, number=1000))
	test()
