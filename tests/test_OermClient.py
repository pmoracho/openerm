import unittest

from openerm.OermClient import OermClient


class OermClientTest(unittest.TestCase):

	def __create_yaml(self, configfile):

		import yaml

		config = {"catalogs": {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True},
							 	"catalogo2": {"name": "Ejemplo catalogo SQL", "type": "sql", "enabled": False}}
		}

		with open(configfile, 'w') as outfile:
			yaml.dump(config, outfile, default_flow_style=True)

	def test_list_catalogs(self):
		"""Verifica la lista de catalogos
		"""
		configfile = 'data.yml'
		self.__create_yaml(configfile)

		# lista = {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True},
		#    		"catalogo2": {"name": "Ejemplo catalogo SQL", "type": "sql", "enabled": False}
		# }

		c = OermClient(configfile)
		# print(c.catalogs())
		self.assertEqual(c.catalogs(), {"catalogo1": {"name": "Ejemplo catalogo local", "type": "path", "enabled": True}})

	def test_open_catalog(self):
		"""Verifica la apertura de catalogos
		"""
		configfile = 'data.yml'
		self.__create_yaml(configfile)

		c = OermClient(configfile)
		c.open_catalog("catalogo1")
		self.assertEqual(c.current_catalog(), {"name": "Ejemplo catalogo local", "type": "path", "enabled": True})
