# -*- coding: utf-8 -*-

"""
# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# report_database.py
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

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def get_key(password):

	digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
	digest.update(password)
	return base64.urlsafe_b64encode(digest.finalize())

def encrypt(password, token):
	f = Fernet(get_key(password))
	return f.encrypt(token)

def decrypt(password, token):
	f = Fernet(get_key(password))
	return f.decrypt(token)


passw = b"es una prueba"
msg = b"Esto es lo que voy a ocultar"

enc = encrypt(passw, msg)
print(enc)

dec = decrypt(passw, enc)
print(dec)




