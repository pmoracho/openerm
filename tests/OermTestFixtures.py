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


class OermTestCatalogFixtures(unittest.TestCase):
	"""Clase para generar un catalogo y repositorio de prueba heredable a los test relacionados"""

	@classmethod
	def _generate_db(cls, compress_method=1,  encription_method=0):
		"""Genera un Database Oerm con info random en un path temporal"""

		# print("OermTestFixtures._generate_db")
		filename = os.path.join(cls._repopath, "test.{0}-{1}.oerm".format(compress_method, encription_method))

		# Primer reporte
		db	= Database(file=filename, mode="wb", default_compress_method=compress_method, default_encription_method=encription_method, pages_in_container=10)
		db.add_report(reporte=cls._reports[0][1], sistema="Sistema 1", aplicacion="Aplicacion 1", departamento="Departamento 1")
		for p in cls._paginas_escritas[:10]:
			db.add_page(p)

		db.close()

		# Segundo reporte
		db	= Database(file=filename, mode="ab", default_compress_method=compress_method, default_encription_method=encription_method, pages_in_container=10)
		db.add_report(reporte=cls._reports[1][1], sistema="Sistema 2", aplicacion="Aplicacion 2", departamento="Departamento 2")
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
		cls._total_pages      = 20
		cls._paginas_escritas = []
		cls._reports          = [(1, 'Reporte 1'), (2, 'Reporte 2')]

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


class OermTestSpoolFixtures(unittest.TestCase):
	"""Clase para generar un spool de prueba heredable a los test relacionados"""

	@classmethod
	def _generate_spool(cls):
		"""Genera un archivo de texto tipo Spool host reprint en una carpeta temporal"""
		def rnd_line_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			"""Genera un string random de determinada longitud"""
			return ''.join(random.choice(chars) for _ in range(size))

		# Crear directorios de trabajo
		cls._startpath   = tempfile.mkdtemp()
		cls._spoolfile   = os.path.join(cls._startpath, "spool.txt")
		cls._total_pages = 10
		cls._paginas     = []

		for i in range(1, cls._total_pages + 1):
			pagina = ""
			pagina = pagina + "1{:10}{:60}Pagina:{:>3}\n".format("Reporte 1", "", i)
			pagina = pagina + " " + 80 * "=" + "\n"

			for j in range(0, 60):
				pagina = pagina + " " + rnd_line_generator(size=80) + "\n"

			cls._paginas.append(pagina)

		with open(cls._spoolfile, "w") as text_file:
			for p in cls._paginas:
				text_file.write(p)

	@classmethod
	def setUpClass(cls):
		cls._generate_spool()

	@classmethod
	def tearDownClass(cls):
		"""Borra completamente los datos generados para el testing"""
		shutil.rmtree(cls._startpath)
