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
	import numpy as np

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


def BoyerMooreHorspool(pattern, text):
	m = len(pattern)
	n = len(text)
	if m > n:
		return -1
	skip = []
	for k in range(256):
		skip.append(m)
	for k in range(m - 1):
		skip[ord(pattern[k])] = m - k - 1
	skip = tuple(skip)
	k = m - 1
	while k < n:
		j = m - 1
		i = k
		while j >= 0 and text[i] == pattern[j]:
			j -= 1
			i -= 1
		if j == -1:
			return i + 1
		k += skip[ord(text[k])]
	return -1

class RollingHash:
	def __init__(self, text, sizeWord):
		self.text = text
		self.hash = 0
		self.sizeWord = sizeWord

		for i in range(0, sizeWord):
			#ord maps the character to a number
			#subtract out the ASCII value of "a" to start the indexing at zero
			self.hash += (ord(self.text[i]) - ord("a")+1)*(26**(sizeWord - i -1))

		#start index of current window
		self.window_start = 0
		#end of index window
		self.window_end = sizeWord

	def move_window(self):
		if self.window_end <= len(self.text) - 1:
			#remove left letter from hash value
			self.hash -= (ord(self.text[self.window_start]) - ord("a")+1)*26**(self.sizeWord-1)
			self.hash *= 26
			self.hash += ord(self.text[self.window_end])- ord("a")+1
			self.window_start += 1
			self.window_end += 1

	def window_text(self):
		return self.text[self.window_start:self.window_end]

def rabin_karp(word, text):
	if word == "" or text == "":
		return None
	if len(word) > len(text):
		return None

	rolling_hash = RollingHash(text, len(word))
	word_hash = RollingHash(word, len(word))
	#word_hash.move_window()

	for i in range(len(text) - len(word) + 1):
		if rolling_hash.hash == word_hash.hash:
			if rolling_hash.window_text() == word:
				return i
		rolling_hash.move_window()
	return None


class ReportMatcher(object):
	"""Matcher de reportes

	Args:
		configfile (string): Path absoluto al archivo de configuración de la clase
		configbuffer (string): Buffer con la configuración YAML de la clase.
		Este parámatro tiene prioridad en caso de ingresar tambioen
		_configfile_

	Example:
		>>> from openerm.ReportMatcher import ReportMatcher
		>>> r = ReportMatcher("../var/reports.yaml")
		>>> print(r.match("R8101611"))

	TODO:
	* orden de matching
	* multiples matches x reporte
	"""
	def __init__(self, configfile="openerm.cfg", configbuffer=None):

		self.config = {}
		self.reports = {}
		self.matches = []
		self.reports = {}
		self.now = datetime.datetime.now().strftime("%Y%m%d")

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

	@staticmethod
	def create_matrix(text, x, y):

		lines = [l.ljust(y)[:y] for l in text.split('\n')]
		if len(lines) > x:
			lines = lines[:x]
		else:
			lines = lines + [''.ljust(y)[:y] for i in range(x-len(lines))]

		return np.array([list(l) for l in lines])


	def _match_report(self, page):

		for reporte, match, box in self.matches:

			if box:
				from_row, from_col, to_row, to_col = box
				print(from_row, from_col, to_row, to_col)

				try:
					matrix = self.create_matrix(page, 300, 300)
				except Exception as exc:
					print(exc)


				print(matrix[from_row-1:to_row, from_col-1:to_col])
				# print(matrix[0:0, 0:5])
				# for l in [line for i, line in enumerate(page.split("\n"),1) if i >= from_row and i <= to_row ]:
				#	slice_line += l[from_col:to_col] + " "
				# text = slice_line
			else:
				text = page
			text = page

			# pos = rabin_karp(match, text)
			# if pos >= 0:
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
