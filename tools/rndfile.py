""
import sys
import re
import re
import os
import time
import datetime
import fnmatch
import getpass
import platform

from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def slugify(text, delim='-'):
	"""Normaliza una cadena para ser usada como nombre de archivo.

	Args:
		text (str): String a normalizar
		delim (str): Caracter de reemplazo de aquellos no válidos

	Ejemplo:
		>>> from openerm.Utils import *
		>>> slugify("Esto, no es válido como nombre de Archivo!", "-")
		'esto-no-es-valido-como-nombre-de-archivo'
	"""
	result = []
	for word in _punct_re.split(text.lower()):
		word = normalize('NFKD', word).encode('ascii', 'ignore')
		word = word.decode('utf-8')
		if word:
			result.append(word)
	return delim.join(result)


def main():

	now = datetime.datetime.now
	path = sys.argv[1]

	fname = slugify(str(now()))
	with open(os.path.join(path, fname), 'w') as f:
		while True:
			f.write(str(now()))
			f.write("\n")
			f.flush()
			time.sleep(5)

	sys.exit(0)


if __name__ == '__main__':
	main()



