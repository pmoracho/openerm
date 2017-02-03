from openerm.OermClient import OermClient
from OermTestFixtures import OermTestCatalogFixtures
from openerm.Block import Block
import os


class OermClientTest(OermTestCatalogFixtures):

	def test_get_catalogs_list(self):
		"""Verifica la lista de catalogos disponibles coincida con la que se acaba de salvar"""
		c = OermClient(self._configfile)
		self.assertEqual(c.catalogs(enabled=None), self.catalog_config)

	def test_get_repos_list(self):
		"""Verifica la lista de repositorios del catalogo"""
		c = OermClient(self._configfile)
		c.open_catalog("catalogo1")
		self.assertEqual(c.repos(), {1: os.path.join(self._repopath, "repo.db")})

	def test_get_reports_list(self):
		"""Verifica la lista de repositorios del catalogo"""
		c = OermClient(self._configfile)
		c.open_catalog("catalogo1")
		c.open_repo(1)
		self.assertEqual(c.reports(), self._reports)

	def test_query(self):
		"""Verifica la consulta de reportes en el repositorio"""
		c = OermClient(self._configfile)
		c.open_catalog("catalogo1")
		c.open_repo(1)
		resultados = c.query_reports(reporte="Reporte 2", returntype="list")

		block = Block()  # Generic

		self.assertEqual(len(resultados), len(block.compressor.available_types))
