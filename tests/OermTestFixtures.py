import os
import tempfile
import yaml
import string
import random
import unittest
import shutil

from openerm.OermClient import OermClient
from openerm.Database import Database
from openerm.Block import Block

class OermTestFixtures(unittest.TestCase):

	@classmethod
	def _generate_db(cls, compress_method=1,  encription_method=0):
		"""Genera un Database Oerm con info random en un path temporal"""

		# print("OermTestFixtures._generate_db")
		filename         = os.path.join(cls._repopath, "test.{0}-{1}.oerm".format(compress_method, encription_method))

		# Primer reporte
		db	= Database(file=filename, mode="wb", default_compress_method=compress_method, default_encription_method=encription_method, pages_in_container=10)
		db.add_report(reporte="Reporte 1", sistema="Sistema 1", aplicacion="Aplicacion 1", departamento="Departamento 1")
		for p in cls._paginas_escritas[:10]:
			db.add_page(p)

		db.close()

		# Segundo reporte
		db	= Database(file=filename, mode="ab", default_compress_method=compress_method, default_encription_method=encription_method, pages_in_container=10)
		db.add_report(reporte="Reporte 2", sistema="Sistema 2", aplicacion="Aplicacion 2", departamento="Departamento 2")
		for p in cls._paginas_escritas[10:]:
			db.add_page(p)

		db.close()

	@classmethod
	def setUpClass(cls):

		# print("OermTestFixtures.setUpClass")
		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		# Crear directorios de trabajo
		cls._startpath        = tempfile.mkdtemp()
		cls._configfile       = os.path.join(cls._startpath, "test.yaml")
		cls._repopath         = os.path.join(cls._startpath, "repo1")
		cls._dbpath           = os.path.join(cls._repopath, "testdb")
		cls._total_pages      = 22
		cls._paginas_escritas = []

		for i in range(1, cls._total_pages + 1):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			cls._paginas_escritas.append(p)

		os.makedirs(cls._repopath)

		# Generar un database
		block = Block()  # Generic

		for item in block.compressor.available_types:
			cls._generate_db(compress_method=item[0])

		# Creo un archivo de configuración para Oerm
		with open(cls._configfile, 'w') as outfile:
			yaml.dump({"catalogs": {}}, outfile, default_flow_style=True)

		# Crear catalogo con el repositorio generado
		c = OermClient(cls._configfile)
		cls.catalog_config = {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True}}
		c.catalog_create(cls.catalog_config)
		c.add_repo("catalogo1", cls._repopath)

	@classmethod
	def tearDownClass(cls):
		"""Borra completamente los datos generados para el testing"""
		# print("OermTestFixtures.tearDownClass")
		shutil.rmtree(cls._startpath)
		pass
