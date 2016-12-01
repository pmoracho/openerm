# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Pages.py
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
Pages
=====

Clase "dummy", pensada eventualmente para el manejo de una colección de páginas.

"""
try:
	import sys
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Pages(object):
	"""Clase "Dummy" para el manejo de páginas"""
	def __init__(self, file, index):

		self.index				= index
		self.file				= file

	def __len__(self):
		return 0

	def __iter__(self):
		return self

	def __next__(self):
		return self
