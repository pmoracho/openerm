# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>

# PageContainer.py

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
PageContainer
=============

Un contenedor de páginas es un objeto que alberga de 1 a N páginas de un reporte. Es
uno de los posibles tipos de Bloque que pueden salvarse en un Database **OpenErm**. La
idea de agrupar varias páginas permite mejorar la performance de los compresores usados
logrando mejores ratios de compresión y por ende reducir el tamaño de los reportes y
el trafico de red o de disco.

.. seealso::
	* :class:`openerm.MetadataContainer`
	* :class:`openerm.PageContainer`

"""

import sys
try:
	import struct
	import gettext

	from gettext import gettext as _
	gettext.textdomain('openerm')

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class PageContainer(object):
	"""Clase base para el manejo de un contenedor de páginas de reportes.Esta clase
	representa un contenedor de páginas, se agrupan las páginas en grupos para mejorar
	los niveles de compresión y de lectura/escritura.

	Args:

		max_page_count (int): Cantidad máxima de página en el contenedor

	Ejemplo:

		>>> from openerm.PageContainer import PageContainer
		>>> p = PageContainer(10)
	"""
	def __init__(self, max_page_count=1):
		self.max_page_count = max_page_count
		self.clear()

	def __len__(self):
		return self.max_page_count

	def __str__(self):
		s = _("[PageContainer]--->\nCantidad máxima de página: {0}\nTotal de páginas		 : {0}\n").format(self.page_count, self.max_page_count)
		for i, p in enumerate(self._pages, 1):
			s += "Pagina: {0}:".format(i)
			s += p
		s += "[PageContainer]--->\n"
		return s

	def __iter__(self):
		return self

	def __next__(self):

		p = self.get_page(self.current_page + 1)
		if not p:
			raise StopIteration

		self.current_page += 1

		return p

	def clear(self):
		"""Limpia la lista interna de páginas

		Ejemplo:

			>>> from openerm.PageContainer import PageContainer
			>>> p = PageContainer(10)
			>>> sample_page = "Pagina de una sola linea"
			>>> p.add(sample_page)
			>>> print(p)
			[PageContainer]--->
			Cantidad máxima de página: 10
			Total de páginas         : 1
			Pagina: 1:Pagina de una sola linea
			[PageContainer]--->
			>>> p.clear()
			>>> print(p)
			[PageContainer]--->
			Cantidad máxima de página: 10
			Total de páginas         : 0
			[PageContainer]--->

		"""
		self._pages			= []
		self.page_count		= 0
		self.current_page	= 0

	def add(self, page):
		"""Agrega una página al grupo. 	Esta rutina agrega un "string" que representa
		la página en el contenedor. La página queda registrada en una lista interna.

		Args:

			page (string): Texto completo de la página a incorporar

		.. error::
				**ValueError**: Cuando se superó la máxima cantidad de páginas del contenedor

		Ejemplo:

			>>> from openerm.PageContainer import PageContainer
			>>> p = PageContainer(10)
			>>> sample_page = "Pagina de una sola linea"
			>>> p.add(sample_page)
			>>> print(p)
			[PageContainer]--->
			Cantidad máxima de página: 10
			Total de páginas		 : 1
			Pagina: 1:Pagina de una sola linea
			[PageContainer]--->

		"""
		if self.page_count >= self.max_page_count:
			raise ValueError(_('Se superó la cantidad máxima de páginas que soporta este PageContainer'))

		self._pages.append(page)
		self.page_count = self.page_count + 1

	def dump(self):
		"""Retorna en bytes el contenido de la lista de páginas del grupo. Este método
		es utilizado cuando construímos el "Bloque" que posteriormente salvaremos en
		un "Database"

		Return:
			tuple:
				- data (bytes)		: Bytes completos de todas las páginas del grupo
				- var_data (bytes)	: Bytes estructurados con los datos para "desarmar" el grupo

		Ejemplo:

			>>> from openerm import PageContainer
			>>> p = PageContainer(10)
			>>> sample_page = "Pagina de una sola linea"
			>>> p.add(sample_page)
			>>> (b'Pagina de una sola linea', b'\x00\x01\x00\x00\x00\x19')

		.. note::
			El método *dump* entrega una estructura como el siguiente ejemplo:

			.. code-block:: python

				+=============+
				|    Datos    | --> Comprimibles
				+=============+
					+=============+
					| Pagina 1    |
					+=============+
					+=============+
					| Pagina "N"  |
					+=============+
				+=============+
				|    Datos    | --> No comprimibles
				| Adicionales |
				+=============+
					+==============+================+    +================+
					| Cant.Paginas | Long. Pagina 1 | .. | Long. Pagina N |
					+==============+================+    +================+

		"""
		data = b''
		for p in self._pages:
			data += p.encode("latin1")

		a_list = [len(p) for p in self._pages]
		ln = len(a_list)

		var_data	= b''
		var_data	+= struct.pack('>H', len(self._pages))
		var_data	+= struct.pack('>' + 'L'*ln, *a_list)
		data		= struct.pack('>{0}s'.format(len(data)), data)
		return (data, var_data)

	def load(self, container_data):
		"""Recupera de un conjunto de bytes cada una de las páginas y construye la lista de las mismas

		Args:

			container_data (bytes): Bytes completos de todas las páginas del grupo. Ver :py:meth:`dump`

		Ejemplo:

			>>> from openerm import PageContainer
			>>> p = PageContainer(10)
			>>> data = (b'Pagina de una sola linea', b'\x00\x01\x00\x00\x00\x19')
			>>> p.load(data)
		"""

		self.clear()

		(data, var_data) 	= container_data
		self.max_page_count	= struct.unpack(">H", var_data[0:2])[0]
		pages_lenght		= struct.unpack('>'+'L'*self.max_page_count, var_data[2:])

		off = 0
		for l in pages_lenght:
			page = data[off:off+l]
			off += l
			self.add(page.decode("latin1"))

	def get_page(self, pagenum):
		"""Retorna una página determinada del grupo.

		Args:
			pagenum (int): Número de página a recupear

		Return:
			(string): Pagina o `None`

		Ejemplo
			>>> import string
			>>> import random
			>>> from openerm.PageContainer import PageContainer
			>>> def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
					return ''.join(random.choice(chars) for _ in range(size))
			>>> pgroup = PageContainer(10)
			>>> for i in range(1,11):
					random_text = rnd_generator(size=200*60)
					pgroup.add(random_text)
			>>> print(pgroup.get_page(5))

		"""
		if pagenum > self.max_page_count:
			return None
		else:
			return self._pages[pagenum - 1]
