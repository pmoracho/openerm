import unittest
import os
import tempfile
import yaml
from openerm.OermClient import OermClient
from openerm.Database import Database


class OermClientTest(unittest.TestCase):

	# def test_catalogs(self):
	# 	"""Verifica la lista de catalogos
	# 	"""

	# 	# lista = {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True},
	# 	#			"catalogo2": {"name": "Ejemplo catalogo SQL", "type": "sql", "enabled": False}
	# 	# }

	# 	c = OermClient(self._configfile)
	# 	# print(c.catalogs())
	# 	self.assertEqual(c.catalogs(), {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True}})

	def test_catalogs(self):
		"""Verifica la lista de catalogos disponibles coincida con la que se acaba de salvar"""

		c = OermClient(self._configfile)
		self.assertEqual(c.catalogs(enabled=None), self.catalog_config)

	def test_open_catalog(self):
		"""Verifica repositorios de un catalogo"""

		c = OermClient(self._configfile)
		c.open_catalog("catalogo1")

		self.assertEqual(c.repos(), {1: os.path.join(self._repopath,"repo.db")})

	@classmethod
	def _generate_db(cls, path):

		filename			= "{0}/test.oerm".format(path)

		import string
		import random

		def rnd_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

		total_pages      = 11
		paginas_escritas = []

		# Primer reporte
		db	= Database(file=filename, mode="wb", default_compress_method=1, default_encription_method=0, pages_in_container=10)
		db.add_report(reporte="Reporte 1", sistema="Sistema 1", aplicacion="Aplicacion 1", departamento="Departamento 1")
		for i in range(1, total_pages + 1):
			random_text = rnd_generator(size=200*60)
			p = "Pagina {0} -----------------\n{1}\nPagina {0} -----------------\n".format(i, random_text)
			paginas_escritas.append(p)
			db.add_page(p)

		db.close()

	@classmethod
	def setUpClass(cls):

		# Crear directorios de trabajo
		cls._startpath = tempfile.mkdtemp()
		cls._configfile = os.path.join(cls._startpath, "test.yaml")
		cls._repopath = os.path.join(cls._startpath, "repo1")
		cls._dbpath = os.path.join(cls._repopath, "testdb")
		os.makedirs(cls._repopath)

		# Generar un database
		cls._generate_db(cls._repopath)

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
		pass
