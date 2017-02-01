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
	"""Clase para generar spooles de prueba heredable a los test relacionados"""

	@classmethod
	def _generate_spools(cls):
		"""	Genera:

			* un archivo de texto tipo Spool host reprint
			* un archivo ebcdic

		Todo en una carpeta temporal.
		"""
		def rnd_line_generator(size=1024, chars=string.ascii_uppercase + string.digits):
			"""Genera un string random de determinada longitud"""
			return ''.join(random.choice(chars) for _ in range(size))

		for i in range(1, cls._total_pages + 1):
			pagina = ""
			pagina = pagina + "1{:9}{:>60}Pagina:{:>3}".format("Reporte 1", "", i) + "\n"
			pagina = pagina + " " + 80 * "=" + "\n"

			for j in range(0, 60):
				pagina = pagina + " " + rnd_line_generator(size=80) + "\n"

			cls._paginas.append(pagina)

		for (k,v) in cls._spools.items():
			filename = os.path.join(cls._startpath, "{0}.spool".format(k))
			v["filename"] = filename
			v["wfunction"]()

	@classmethod
	def _SpoolHostReprint_Save(cls):

		file_name = cls._spools['SpoolHostReprint'].get("filename")
		with open(file_name, "w") as text_file:
			for p in cls._paginas:
				text_file.write(p)

	@classmethod
	def _SpoolFixedRecordLength_Save(cls):

		file_name = cls._spools['SpoolFixedRecordLength'].get("filename")
		# with open(file_name, "w") as text_file:
		with open(file_name, "w", encoding="cp500") as text_file:
			for p in cls._paginas:
				for l in p.split("\n"):
					if l:
						text_file.write('{:132}'.format(l))

	@classmethod
	def setUpClass(cls):
		# Crear directorios de trabajo
		cls._startpath   = tempfile.mkdtemp()
		cls._total_pages = 10
		cls._paginas     = []
		cls._spools  	 = {
						'SpoolHostReprint': {"wfunction": cls._SpoolHostReprint_Save, "filename": ""} ,
						'SpoolFixedRecordLength': {"wfunction": cls._SpoolFixedRecordLength_Save, "filename": ""}
					  }

		cls._generate_spools()

	@classmethod
	def tearDownClass(cls):
		"""Borra completamente los datos generados para el testing"""
		# print(cls._startpath)
		shutil.rmtree(cls._startpath)
