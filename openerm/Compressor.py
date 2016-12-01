# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Compressor.py
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
Compressor
==========

Esta clase gestiona los algoritmos de compresión que se pueden utilizarse en un
:class:`openerm.Database` OERM. Este objeto ofrece dos rutinas básicas:

	* :py:func:`compress`
	* :py:func:`decompress`

y dos posibles formas de configurar estos metódos en la inicialización del
objeto:

	* **type**: Tipo de compresión
	* **level**: Nivel de compresión  0=mínimo/rápido, 1=normal/estándar,2=máximo/lento


Tipos/Algoritmos de compresión
==============================

	==== ================================================
	Tipo Detalle
	==== ================================================
	0    Sin compresión
	1    **Gzip** es una abreviatura de GNU ZIP, un software libre GNU que reemplaza al programa compress de UNIX. gzip fue creado por Jean-loup Gailly y Mark Adler. Apareció el 31 de octubre de 1992 (versión 0.1). La versión 1.0 apareció en febrero de 1993. Gzip se basa en el algoritmo Deflate, que es una combinación del LZ77 y la codificación Huffman. Deflate se desarrolló como respuesta a las patentes que cubrieron LZW y otros algoritmos de compresión y limitaba el uso del compress.
	2    **Bzip2** es un programa libre desarrollado bajo licencia BSD que comprime y descomprime ficheros usando los algoritmos de compresión de Burrows-Wheeler y de codificación de Huffman. El porcentaje de compresión alcanzado depende del contenido del fichero a comprimir, pero por lo general es bastante mejor al de los compresores basados en el algoritmo LZ77/LZ78 (gzip, compress, WinZip, pkzip,...). Como contrapartida, bzip2 emplea más memoria y más tiempo en su ejecución.
	3    **LZMA** El Algoritmo de cadena de Lempel-Ziv-Markov o LZMA es un algoritmo de compresión de datos en desarrollo desde 1998. Se utiliza un esquema de compresión diccionario algo similar a LZ77, cuenta con una alta relación de compresión y una compresión de tamaño variable diccionario (de hasta 4 GB). Se utiliza en el formato 7z del archivador 7-Zip.
	4    **LZ4** is lossless compression algorithm, providing compression speed at 400 MB/s per core (0.16 Bytes/cycle). It features an extremely fast decoder, with speed in multiple GB/s per core (0.71 Bytes/cycle). A high compression derivative, called LZ4_HC, is available, trading customizable CPU time for compression ratio. LZ4 library is provided as open source software using a BSD license.
	5    **pyLZMA**, otra implementación de **LZMA**
	6    **BLOSC** an extremely fast, multi-threaded, meta-compressor library
	7    **Snappy** (previously known as Zippy) is a fast data compression and decompression library written in C++ by Google based on ideas from LZ77 and open-sourced in 2011. It does not aim for maximum compression, or compatibility with any other compression library; instead, it aims for very high speeds and reasonable compression
	8    **Lzo** or Lempel–Ziv–Oberhumer is a lossless data compression algorithm that is focused on decompression speed
	9    **Brotli** es una librería de compresión de datos de código abierto desarrollada por Jyrki Alakuijala y Zoltán Szabadka.1 2 Brotli está basado en una variante moderna del algoritmo LZ77, codificación Huffman y modelado de contexto de segundo orden.
	10   **Zstandard**, or zstd as short version, is a fast lossless compression algorithm, targeting real-time compression scenarios at zlib-level and better compression ratios.
	==== ================================================


Descripción de la clase
=======================
"""


try:

	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	# import base64
	# import struct
	# import os

	import lzo
	import zlib
	import bz2
	import lzma
	import snappy
	import blosc
	import lz4
	import pylzma
	import brotli
	import zstd

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Compressor(object):
	"""
	Clase base para el manejo de compresión/descompresión de "bytes".

	Esta es una clase base para poder configurar distintos algoritmos de
	compresión, pero que a la vez ofrezca una interfaz común para comprimir
	y descomprimir.

	Args:
		compress_type  (int): Tipo de compresión
		level (int): Nivel de compresión 0=mínimo, 1=normal, 2=máximo

	Example:
		>>> from openerm.Compressor import Compressor
		>>> c = Compressor(compress_type=1, level=1)
		>>> tmp = c.compress(b"Esta es una prueba")
		>>> print(tmp)
		b'x^s-.ITH-V(\xcdKT((*MMJ\x04\x00<}\x06\x89'
	"""
	def __init__(self, compress_type=1, level=1):

		self._levels = {
				0: (0, 0, 0),
				1: (1, 6, 9),
				2: (1, 6, 9),
				3: (0, 6, 9),
				4: (0, 6, 9),
				5: (0, 1, 2),
				6: (1, 6, 9),
				7: (0, 0, 0),
				8: (1, 2, 9),
				9: (1, 2, 11),
				10: (1, 3, 22),
		}

		self._compression_level = self._levels[compress_type][level]
		self._compression_proc_function = {
						0: (self._plain_data_compress,			self._plain_data_decompress,		_("Sin compression")),
						1: (self._zlib_compress,				zlib.decompress,					_("GZIP level={0} (1-9)").format(self._levels[1][level])),
						1: (self._zlib_compress,				zlib.decompress,					_("GZIP level={0} (1-9)").format(self._levels[1][level])),
						2: (self._bz2_compress,					bz2.decompress,						_("BZIP level={0} (1-9)").format(self._levels[2][level])),
						3: (self._lzma_compress,				lzma.decompress,					_("LZMA preset={0} (0-9) ").format(self._levels[3][level])),
						4: (self._lz4_compress, 				lz4.decompress,						_("LZ4 nivel estándar")),
						5: (self._pylzma_compress,				pylzma.decompress,					_("pyLZMA quality={0} (0-2)").format(self._levels[5][level])),
						6: (self._blosc_compress,				blosc.decompress,					_("BLOSC blosclz clevel={0} (1-9)").format(self._levels[6][level])),
						7: (snappy.compress,					snappy.decompress,					_("Snappy")),
						8: (self._lzo_compress,					lzo.decompress,						_("Lzo level={0} (1-9)").format(self._levels[8][level])),
						9: (self._brotli_best_compress,			brotli.decompress,					_("Brotli quality={0} (1-11)").format(self._levels[9][level])),
						10: (self._zstd_compress,				zstd.decompress,					_("zstd level={0} (1-22)").format(self._levels[10][level]))
					}

		self.__compression_type = compress_type

	@property
	def type(self):
		"""Tipo de compresión (algorimo) a utilizar.

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor()
			>>> print(c.type)
			1
		"""
		return self.__compression_type

	@type.setter
	def type(self, compress_type):
		"""
		type. Configura el tipo de compresión a utilizar.
		"""
		if compress_type != self.__compression_type:
			if compress_type not in self._compression_proc_function.keys():
				self.__compression_type = 1
			else:
				self.__compression_type = compress_type

	@property
	def level(self):
		"""Nivel de compresión a utilizar

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor()
			>>> print(c.level)
			1

		"""
		return self._compression_level

	@level.setter
	def level(self, level):
		"""Nivel de compresión a utilizar

		Args:
			level (int): Nivel de compresión 0=mínimo, 1=normal, 2=máximo

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor()
			>>> c.level = 2
		"""
		if level != self._compression_level:
			if level not in [0, 1, 2]:
				self._compression_level = 1
			else:
				self._compression_level = level

	@property
	def available_types(self):
		"""Retorna los tipos de compresión disponibles.

		Returns:
			Lista de algoritmos disponibles.

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor()
			>>> for c in c.available_types:
			...     print(c)
			...
			(0, 'Sin compression')
			(1, 'GZIP level=6 (1-9)')
			(2, 'BZIP level=6 (1-9)')
			(3, 'LZMA preset=6 (0-9) ')
			(4, 'LZ4 nivel estándar')
			(5, 'pyLZMA quality=1 (0-2)')
			(6, 'BLOSC blosclz clevel=6 (1-9)')
			(7, 'Snappy')
			(8, 'Lzo level=2 (1-9)')
			(9, 'Brotli quality=2 (1-11)')
			(10, 'zstd level=3 (1-22)')
			>>>
		"""
		return [(i, self._compression_proc_function[i][2]) for i in self._compression_proc_function]

	def compression_type_info(self, compress_type):
		"""Retorna la información de un determinado
		algoritmo de compressión disponible.

		Args:
			compress_type (int): Id del algoritmo de compresión

		Returns:
			string: Información del algoritmo de compresión

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor()
			>>> print(c.compression_type_info(10))
			zstd level=3 (1-22)

		"""
		return self._compression_proc_function[compress_type][2]

	def compress(self, data):
		"""Comprime un conjunto de bytes

		Args:
			data: (bytes) conjunto de bytes a comprimir

		Returns:
			bytes comprimidos.

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor(compress_type=1, level=1)
			>>> tmp = c.compress(b"Esta es una prueba")
			>>> print(tmp)
			b'x^s-.ITH-V(\xcdKT((*MMJ\x04\x00<}\x06\x89'
		"""
		return self._compression_proc_function[self.__compression_type][0](data)

	def decompress(self, data):
		"""Descomprime un conjunto de bytes

		Args:
			data: (bytes) conjunto de bytes comprimidos

		Returns:
			bytes descomprimidos.

		Example:
			>>> from openerm.Compressor import Compressor
			>>> c = Compressor(compress_type=1, level=1)
			>>> tmp = c.compress(b"Esta es una prueba")
			>>> print(tmp)
			b'x^s-.ITH-V(\xcdKT((*MMJ\x04\x00<}\x06\x89'
			>>> print(c.decompress(tmp))
			b'Esta es una prueba'
		"""
		return self._compression_proc_function[self.__compression_type][1](data)

	def _zlib_compress(self, data):
		return zlib.compress(data, self._compression_level)

	def _bz2_compress(self, data):
		return bz2.compress(data, self._compression_level)

	def _blosc_compress(self, data):
		"""
		compress(bytesobj[, typesize=8, clevel=9, shuffle=blosc.SHUFFLE, cname='blosclz']])

		Compress bytesobj, with a given type size.

		Parameters
		----------
		bytesobj :	bytes-like object (supporting the buffer interface)
					The data to be compressed.
		typesize :	int
					The data type size.
		clevel	 :	int (optional)
					The compression level from 0 (no compression) to 9
					(maximum compression).	The default is 9.
		shuffle  :	int (optional)
					The shuffle filter to be activated.  Allowed values are
					blosc.NOSHUFFLE, blosc.SHUFFLE and blosc.BITSHUFFLE.  The
					default is blosc.SHUFFLE.
		cname	 :	string (optional)
					The name of the compressor used internally in Blosc.
					It can be any of the supported by Blosc ('blosclz',
					'lz4', 'lz4hc', 'snappy', 'zlib' and maybe others too).
					The default is 'blosclz'.
		"""
		# return blosc.compress(data, typesize=8, cname='blosclz')
		return blosc.compress(data, typesize=8, clevel=self._compression_level, cname='blosclz')

	@staticmethod
	def _plain_data_compress(data):
		return data

	@staticmethod
	def _plain_data_decompress(data):
		return data

	@staticmethod
	def _lz4_compress(data):
		"""Compresión Lz4
		Args:
			source (str): Data to compress
			mode (str): If 'default' or unspecified use the default LZ4
				compression mode. Set to 'fast' to use the fast compression
				LZ4 mode at the expense of compression. Set to
				'high_compression' to use the LZ4 high-compression mode at
				the exepense of speed
			acceleration (int): When mode is set to 'fast' this argument
				specifies the acceleration. The larger the acceleration, the
				faster the but the lower the compression. The default
				compression corresponds to a value of 1.
			compression (int): When mode is set to `high_compression` this
				argument specifies the compression. Valid values are between
				0 and 16. Values between 4-9 are recommended, and 0 is the
				default.
		Returns:
			str: Compressed data
		"""
		return lz4.compress(data)

	def _lzma_compress(self, data):
		"""Compresión lzma
		compress(data, format=1, check=-1, preset=None, filters=None)
		Compress a block of data.

		The format argument specifies what container format should be used. Possible values are:
		FORMAT_XZ: The .xz container format.
		This is the default format.
		FORMAT_ALONE: The legacy .lzma container format.
		This format is more limited than .xz – it does not support integrity checks or multiple filters.
		FORMAT_RAW: A raw data stream, not using any container format.
		This format specifier does not support integrity checks, and requires that you always specify a custom filter chain (for both compression and decompression). Additionally, data compressed in this manner cannot be decompressed using FORMAT_AUTO (see LZMADecompressor).

		The check argument specifies the type of integrity check to include in the compressed data. This check is used when decompressing, to ensure that the data has not been corrupted. Possible values are:
		CHECK_NONE: No integrity check. This is the default (and the only acceptable value) for FORMAT_ALONE and FORMAT_RAW.
		CHECK_CRC32: 32-bit Cyclic Redundancy Check.
		CHECK_CRC64: 64-bit Cyclic Redundancy Check. This is the default for FORMAT_XZ.
		CHECK_SHA256: 256-bit Secure Hash Algorithm.
		If the specified check is not supported, an LZMAError is raised.

		The compression settings can be specified either as a preset compression level (with the preset argument), or in detail as a custom filter chain (with the filters argument).
		The preset argument (if provided) should be an integer between 0 and 9 (inclusive), optionally OR-ed with the constant PRESET_EXTREME. If neither preset nor filters are given, the default behavior is to use PRESET_DEFAULT (preset level 6). Higher presets produce smaller output, but make the compression process slower.


		"""
		return lzma.compress(data, preset=self._compression_level)

	def _pylzma_compress(self, data):
		"""Compresión pylzma
		dictionary
		Dictionary size (Range 0-28, Default: 23 (8MB))
		The maximum value for dictionary size is 256 MB = 2^28 bytes. Dictionary size is calculated as DictionarySize = 2^N bytes. For decompressing file compressed by LZMA method with dictionary size D = 2^N you need about D bytes of memory (RAM).

		fastBytes
		Range 5-255, default 128
		Usually big number gives a little bit better compression ratio and slower compression process.

		literalContextBits
		Range 0-8, default 3
		Sometimes literalContextBits=4 gives gain for big files.

		literalPosBits
		Range 0-4, default 0
		This switch is intended for periodical data when period is equal 2^N. For example, for 32-bit (4 bytes) periodical data you can use literalPosBits=2. Often it's better to set literalContextBits=0, if you change the literalPosBits switch.

		posBits
		Range 0-4, default 2
		This switch is intended for periodical data when period is equal 2^N.

		algorithm
		Compression mode 0 = fast, 1 = normal, 2 = max (Default: 2)
		The lower the number specified for algorithm, the faster compression will perform.

		multithreading
		Use multithreading if available? (Default yes)
		Currently, multithreading is only available on Windows platforms.

		eos
		Should the End Of Stream marker be written? (Default yes) You can save some bytes if the marker is omitted, but the total uncompressed size must be stored by the application and used when decompressing:
		"""
		return pylzma.compress(data, algorithm=self._compression_level)

	def _brotli_best_compress(self, data):
		"""brotli.compress(data, mode=<BrotliEncoderMode.GENERIC: 0>, quality=11, lgwin=22, lgblock=0, dictionary='')

		mode		(BrotliEncoderMode or int) – The encoder mode.
		quality		(int) – Controls the compression-speed vs compression-density tradeoffs. The higher the quality, the slower the compression. The range of this value is 0 to 11.
		lgwin		(int) – The base-2 logarithm of the sliding window size. The range of this value is 10 to 24.
		lgblock		(int) – The base-2 logarithm of the maximum input block size. The range of this value is 16 to 24. If set to 0, the value will be set based on quality.
		dictionary	(bytes) – A pre-set dictionary for LZ77. Please use this with caution: if a dictionary is used for compression, the same dictionary must be used for decompression!
		"""
		return brotli.compress(data, quality=self._compression_level)

	def _lzo_compress(self, data):
		"""Compresión lzo
		compress(string[,level[,header]]) -- Compress string, returning a string containing compressed data.
		level  - Set compression level of either 1 (default) or 9.
		header - Include metadata header for decompression in the output (default: True).
		"""
		return lzo.compress(data, self._compression_level)

	def _zstd_compress(self, data):
		"""Compresión zstd

		Param: Level -> 0-22
		"""
		return zstd.compress(data, self._compression_level)

	def _get_compression_proc_function_help(self, compression_method):
		return self.compression_proc_function[compression_method](2)
