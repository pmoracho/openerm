# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Cipher.py
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

try:

	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	import base64
	# import os
	# import struct
	# import hashlib

	from openerm.Spritz import Spritz
	# from openerm.simple_rsa	import *
	# from cryptography.fernet import Fernet, MultiFernet
	from cryptography.fernet import Fernet
	from cryptography.hazmat.backends import default_backend
	from cryptography.hazmat.primitives import hashes
	from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Cipher(object):
	"""Clase base para el manejo de cifrado de "bytes".

	Esta es una clase base para poder configurar distintos algoritmos de
	cifrado, pero que a la vez ofrezca una interfaz común para cifrar
	y descifrar.

	Args:
		type (int): Opcional, Tipo de cifrado por defecto (default=0-Ninguno)

	Example:
		>>> from openerm.Cipher import Cipher
		>>> c = Cipher(type=2)
		>>> tmp = c.encode(b'esto es una prueba')
		>>> print(tmp)
		b'gAAAAABX2dYtQhe7Th3sA24606o_747bts4n11Jm37gHW5SIRanP105loH4jPBJzEPrlBmhb9ai5FcXIBhTtUswHA_H6yrzgVK0CPDig0iSKQjyfaWJryJI='
	"""
	def __init__(self, type=0):

		self._cipher_proc_function = {
						0: (self._init_none, 	self._encode_decode_none,			self._encode_decode_none,				_("Sin encriptación")),
						1: (self._init_spritz,	self._encode_spritz,				self._decode_spritz,					_("Spritz")),
						2: (self._init_fernet,	self._encode_fernet,				self._decode_fernet,					_("Fernet"))
					}

		self._type		= type
		self._fernet	= None
		self.key		= None
		self.spritz		= None

		self._cipher_proc_function[self._type][0]()

	def _init_none(self):
		pass

	def _init_spritz(self):
		self.spritz		= Spritz()
		self.key		= "mysecretpassword"

	def _init_fernet(self):
		self.password	= b"password"
		# salt = os.urandom(16)
		salt = b'\xb8\x81)\x13\xd3\xfc\x8c\x97\xe1\xc1[\xd5\xed\x18\x93!'
		kdf = PBKDF2HMAC(	algorithm=hashes.SHA256(),
							length=32,
							salt=salt,
							iterations=100000,
							backend=default_backend()
						)
		key = base64.urlsafe_b64encode(kdf.derive(self.password))
		self._fernet = Fernet(key)

	@property
	def type(self):
		"""Tipo de cifrado.
		"""
		return self._type

	@type.setter
	def type(self, type):
		"""Tipo de cifrado a utilizar.

		Example:
			>>> from openerm.Cipher import Cipher
			>>> c = Cipher()
			>>> print(c.type)
			1
		"""
		if type != self._type:
			if type not in self._cipher_proc_function.keys():
				self._type = 0
			else:
				self._type = type

			self._cipher_proc_function[self._type][0]()

	@property
	def available_types(self):
		"""Retorna los tipos de cifrados disponibles.

		Returns:
			list: Lista de algoritmos cifrados.

		Example:
			>>> from openerm.Cipher import Cipher
			>>> c = Cipher()
			>>> c.available_types
			[(0, 'Sin encriptación'), (1, 'Spritz'), (2, 'Fernet')]
		"""
		return [(i, self._cipher_proc_function[i][3]) for i in self._cipher_proc_function]

	def type_info(self, type):
		"""Retorna la información de un determinado algoritmo de cifrado disponible.

		Returns:
		(tupla).
		"""
		if type not in self._cipher_proc_function.keys():
			return (type, _("Algoritmo no disponible"))
		else:
			return (type, self._cipher_proc_function[type][3])

	def encode(self, data):
		"""Cifra conjunto de bytes

		Args:
			data (bytes): conjunto de bytes a cifrar

		Returns:
			bytes: datos cifrados.

		Example:
			>>> from openerm.Cipher import Cipher
			>>> c = Cipher(type=2)
			>>> tmp = c.encode(b'esto es una prueba')
			>>> print(tmp)
			b'gAAAAABX2dYtQhe7Th3sA24606o_747bts4n11Jm37gHW5SIRanP105loH4jPBJzEPrlBmhb9ai5FcXIBhTtUswHA_H6yrzgVK0CPDig0iSKQjyfaWJryJI='
		"""
		return self._cipher_proc_function[self._type][1](data)

	def decode(self, data):
		"""Descifra un conjunto de bytes

		Args:
			data (bytes): conjunto de bytes cifrados

		Returns:
			bytes: datos descifrados.

		Example:
			>>> from openerm.Cipher import Cipher
			>>> c = Cipher(type=2)
			>>> tmp = c.encode(b'esto es una prueba')
			>>> print(tmp)
			b'gAAAAABX2dYtQhe7Th3sA24606o_747bts4n11Jm37gHW5SIRanP105loH4jPBJzEPrlBmhb9ai5FcXIBhTtUswHA_H6yrzgVK0CPDig0iSKQjyfaWJryJI='
			>>> print(c.decode(tmp))
			b'esto es una prueba'
		"""
		return self._cipher_proc_function[self._type][2](data)

	def _encode_decode_none(self, data):
		return data

	def _encode_fernet(self, clear):
		enc = self._fernet.encrypt(clear)
		return enc

	def _decode_fernet(self, enc):
		return self._fernet.decrypt(enc)

	def _encode_spritz(self, clear):
		return bytes(self.spritz.encrypt(bytearray(self.key.encode("utf-8")), bytearray(clear)))

	def _decode_spritz(self, enc):
		return bytes(self.spritz.decrypt(bytearray(self.key.encode("utf-8")), bytearray(enc)))

	def _encode_rsa(self, clear):
		return self.encode(clear, self.pubkey, False)

	def _decode_rsa(self, enc):
		return self.decode(enc, self.privkey, False)