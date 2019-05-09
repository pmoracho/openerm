# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Block.py
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
Block
=====

Un "bloque" de datos. Un Block es la unidad miníma de un Database OERM. Hay dos
tipos de bloque básico:

	* :class:`openerm.MetadataContainer` para guardar los atributos de un
		determinado reporte.  
	* :class:`openerm.PageContainer` para guardar conjuntos de páginas

.. seealso::
	* :class:`openerm.Database`
	* :class:`openerm.Compressor`
	* :class:`openerm.Cipher`

"""

try:

	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	import struct

	from openerm.Compressor import Compressor
	from openerm.Cipher import Cipher

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Block(object):
	"""Bloque de un archivo OpenERM. El bloque es la unidad mínima de
	información. Existen en está versión dos tipo de bloques básicos:

		- Contenedores de metadatos
		- Contenedores de páginas

	Cada bloque puede o no ser comprimido y encriptado con algún algoritmo que
	dependerá de la implememntación OpenERM particular.

	Args:
		default_compress_method (int): Compresión por defecto del bloque (default = 1 - Gzip)
		default_compress_level (int): Nivel de compresión por defecto del bloque (default = 1 Medium)
		default_encription_method (int): Algoritmo de cifrado (0 = Ninguno)

	"""
	def __init__(	self,
			  default_compress_method=1,
			  default_compress_level=1,
			  default_encription_method=0
			  ):

		self.compressor	= Compressor(default_compress_method, default_compress_level)
		self.cipher		= Cipher(default_encription_method)

		#: Tipos de bloque
		#: 	1 - Report metadata
		#:	2 - Pages container
		self.block_types = {
			1: "Report metadata",
			2: "Pages container"
		}

	def dump(self, tipo_bloque, data, variable_data=None):
		"""Convierte los datos en un bloque OpenErm que puede ser "salvable" en un archivo

		Args:
			tipo_bloque (int): Tipo de bloqe (1: metadatos, 2: páginas)
			data (bytes): Bytes de los datos a salvar
			variable_data (bytes): (opcional) Datos adicionales, es información que se salva en el bloque pero no se comprime

		Example:
			>>> from openerm.Block import Block
			>>> b = Block(default_compress_method=1, default_compress_level=1, default_encription_method=0)
			>>> data = b.dump(tipo_bloque=2, data=b"Esto hace las veces de una pagina de reporte",variable_data=None)
			>>> print(data)
			b'\x00\x00\x00<\x02\x01\x00\x00\x00\x001x\x9cs-.\xc9W\xc8HLNU\xc8I,V(KMN-VHIU(\xcdKT(HL\xcf\x04R@^QjA~QI*\x00]\x1f\x0f\xca'

		.. note::
			El método *dump* entrega una estructura como el siguiente ejemplo:

			.. code-block:: python

				+=======================+
				| Long.Total del Bloque |   --> long (4 bytes)
				+=======================+
				| Tipo de Bloque  |         --> int (1 bytes)
				+=================+
				| Alg. Compresión |         --> int (1 bytes)
				+=================+
				| Alg. Cifrado    |         --> int (1 bytes)
				+=======================+
				| Long. de los Datos    |   --> long (4 bytes)
				+=======================+
				|                       |
				|        Datos          |   --> Longitud variable (datos comprimibles)
				|                       |
				+=======================+
				|                       |
				|    Datos variables    |   --> (Opcional) Longitud variable (datos NO comprimibles)
				|                       |
				+=======================+

		"""

		struct_fmt	= ">LBBBL"
		data		= self.compressor.compress(data)
		data		= self.cipher.encode(data)

		l_data		= len(data)
		struct_fmt	= struct_fmt + "{0}s".format(l_data)

		if variable_data:
			struct_fmt	= struct_fmt + "{0}s".format(len(variable_data))
			b			= struct.pack(	struct_fmt,
					 struct.calcsize(struct_fmt),	# Longitud total del bloque
					 tipo_bloque,					# Tipo de objeto
					 self.compressor.type,			# Metodo de compresión
					 self.cipher.type,				# Metodo de encriptación
					 l_data,						# Longitud del contenido
					 data,							# Contenido
					 variable_data					# Datos variables
					 )
		else:
			b			= struct.pack(	struct_fmt,
					 struct.calcsize(struct_fmt),	# Longitud total del bloque
					 tipo_bloque,					# Tipo de objeto
					 self.compressor.type,			# Metodo de compresión
					 self.cipher.type,				# Metodo de encriptación
					 l_data,						# Longitud del contenido
					 data							# Contenido
					 )

		return b

	def load(self, data):
		"""Convierte un bloque OpenErm en datos lógicos

		Args:
			data (bytes): Bytes del bloque completo

		Return:
			tuple

		Se devuelve una "tupla" de 7 elementos:

		========= ================================================
		Tipo	  Detalle
		========= ================================================
		long      Longitud total del bloque incluído este dato
		int       Tipo de bloque
		int       Tipo de compresión
		int       Tipo de encriptado
		long      longitud de los datos comprimidos
		bytes     Datos
		bytes     Datos adicionales
		========= ================================================


		Example:
			>>> from openerm.Block import Block
			>>> b = Block(default_compress_method=1, default_compress_level=1, default_encription_method=0)
			>>> data = b.dump(tipo_bloque=2, data=b"Esto hace las veces de una pagina de reporte",variable_data=None)
			>>> print(data)
			b'\x00\x00\x00<\x02\x01\x00\x00\x00\x001x\x9cs-.\xc9W\xc8HLNU\xc8I,V(KMN-VHIU(\xcdKT(HL\xcf\x04R@^QjA~QI*\x00]\x1f\x0f\xca'
			>>> print(b.load(data))
			(60, 2, 1, 0, 49, b'Esto hace las veces de una pagina de reporte', None)
		"""

		# Obtener datos iniciales del bloque
		struct_fmt			= ">LBBBL"
		header_len			= struct.calcsize(struct_fmt)
		struct_unpack		= struct.Struct(struct_fmt).unpack_from

		fields				= struct_unpack(data[0:header_len])

		longitud_bloque		= fields[0]
		tipo_bloque			= fields[1]
		tipo_compresion		= fields[2]
		tipo_encriptacion	= fields[3]
		longitud_datos		= fields[4]

		longitud_datos_variables = longitud_bloque - (header_len + longitud_datos)

		struct_fmt	= "{0}s".format(longitud_datos)

		if longitud_datos_variables > 0:
			struct_fmt			= struct_fmt + "{0}s".format(longitud_datos_variables)
			struct_unpack		= struct.Struct(struct_fmt).unpack_from
			fields				= struct_unpack(data[header_len:])
			data				= fields[0]
			variable_data		= fields[1]
		else:
			struct_unpack		= struct.Struct(struct_fmt).unpack_from
			fields				= struct_unpack(data[header_len:])
			data				= fields[0]
			variable_data		= None

		self.compressor.type 	= tipo_compresion
		self.cipher.type 		= tipo_encriptacion
		data 					= self.compressor.decompress(self.cipher.decode(data))

		return (longitud_bloque, tipo_bloque, tipo_compresion, tipo_encriptacion, longitud_datos, data, variable_data)
