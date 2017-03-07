# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# metadata_container
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
MetadataContainer
=================

Un contenedor de metadatos es un tipo de "bloque" de un Database OpenErm, representa
los atributos que describen el reporte. Cada reporte tiene un conjunto básico y fijo
de atributos y es posible agregar los que deseemos.

.. seealso::
	* :class:`openerm.PageContainer`
	* :class:`openerm.MetadataContainer`

"""
try:
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	import json

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class MetadataContainer(object):
	"""Contenedeor de los "metadatos" del reporte

	Args:
		metadata (dict): Diccionario de los datos fundamentales de un reporte


	"""
	def __init__(self, metadata=None:

		self.metadata    = metadata if metadata else {}
		self.tipo_bloque = 1

	def __str__(self):
		return repr(self.metadata)

	def add(self, extradata):
		"""Agrega un diccionario de datos extra al contenedor

		Args:
			extradata (dict): Datos adicionales

		Ejemplo:
			>>> import datetime
			>>> from openerm.MetadataContainer import MetadataContainer
			>>> now = datetime.datetime.now()
			>>> m = MetadataContainer("Reporte sin identificar", "n/a", "n/a", "n/a", now)
			>>> extra_data = {"autor": "Ernesto Guevara", "Estado": "Draft"}
			>>> m.add(extra_data)
		"""
		self.metadata.update(extradata)

	def dump(self):
		""" Retorna en bytes el contenido de los metadatos ya listos para comprimir y
		eventualmentre salvar físicamente en el Database Oerm. El "dump" termina siendo
		una representación plana de un diccionario de datos en formato JSON. Los datos
		pueden ser variables.

		Ejemplo:
			>>> import datetime
			>>> from openerm.MetadataContainer import MetadataContainer
			>>> now = datetime.datetime.now()
			>>> m = MetadataContainer("Reporte sin identificar", "n/a", "n/a", "n/a", now)
			>>> data = m.dump()
			>>> print(data)
			b'{"departamento": "n/a", "fecha": "20160914", "aplicacion": "n/a", "sistema": "n/a", "reporte": "Reporte sin identificar"}'

		.. note::
			El método *dump* entrega una estructura como el siguiente ejemplo:

			.. code-block:: python

				+=============+
				|    Datos    | --> Comprimibles
				|  Json dump  |
				+=============+

		"""

		return json.dumps(self.metadata).encode("utf-8")

	def load(self, data):
		""" Recupera de un conjunto de bytes los metadatos

		Args:
			data: bytes

		Ejemplo:
			>>> import datetime
			>>> from openerm.MetadataContainer import MetadataContainer
			>>> now = datetime.datetime.now()
			>>> m = MetadataContainer("Reporte sin identificar", "n/a", "n/a", "n/a", now)
			>>> data = m.dump()
			>>> print(data)
			b'{"departamento": "n/a", "fecha": "20160914", "aplicacion": "n/a", "sistema": "n/a", "reporte": "Reporte sin identificar"}'
			>>> m2 = MetadataContainer()
			>>> m2.load(data)
			>>> print(m2)
			{'departamento': 'n/a', 'fecha': '20160914', 'sistema': 'n/a', 'aplicacion': 'n/a', 'reporte': 'Reporte sin identificar'}
		"""
		self.metadata = json.loads(data.decode("utf-8"))

		return self.metadata
