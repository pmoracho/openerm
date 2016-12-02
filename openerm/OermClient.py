# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# OermClient.py
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
OermClient
==========

Un **OermClient** es el objeto que permite conectarse a uno o más repositorios
de reportes. Es la clase "oficial" para acceder a los reportes, conceptualmente
un **OermClient** ofrece uno o más catálogos, los catálogos son organizaciones
lógicas de los reportes físicos


.. seealso::
	* :class:`openerm.MetadataContainer`
	* :class:`openerm.PageContainer`

"""


try:

	import sys
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import yaml
	import os
	import sqlite3
	# from openerm.Utils import *
	from openerm.tabulate import tabulate

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class OermClient(object):
	"""Clase Cliente para acceso a reportes Oerm. Los reportes OERM
	se clasifican en: Catalogos y Repositorios. Un catalogo en
	realidad representa un conjunto lógico de repositorios, los
	repositorios representan carpetas físicas.

	Args:

		configfile (string): Nombre del archivo de configuración (Formato YAML)
	"""
	def __init__(self, configfile=None):

		self._catalogs			= []			#: Lista de catalogos disponibles
		self._repo_catalogs		= []			#: Catalogs de cada repositorio
		self._current_catalog	= {}			#: Catalogo activo
		self.config				= {}
		self.configfile			= configfile
		if configfile:
			self._load_configfile()

	def _load_config(self, yamltext):
		self.config = yaml.load(yamltext)
		self._catalogs = self.config.get("catalogs", {})

	def _load_configfile(self):
		"""Carga la configuración en el diccionario interno de la clase"""
		with open(self.configfile, 'r') as stream:
			try:
				self.config = yaml.load(stream)
			except yaml.YAMLError as exc:
				print(exc)

		self._catalogs = self.config.get("catalogs", {})

	def open_catalog(self, catalogid):
		"""Conexión y apertura de un catalogo

		Args:
			catalogid (string): Id del catalogo que se desea abrir

		Tipos de catalogos:

			- Lista de paths + catalog.db
			- Centralizado en Servidor SQL

		"""
		self._current_catalog = self._catalogs[catalogid]
		self._repo_catalogs	= {}
		if self._current_catalog.get("type", "path"):
			for d in self._current_catalog.get("urls", []):
				(n, p), = d.items()
				self._repo_catalogs.update({n: os.path.join(p, "repo.db")})

	def close_catalog(self, catalog):
		"""Cierra el catalgo activo

		Args:
			catalogid (string): Id del catalogo que se desea cerrar
		"""
		self._current_catalog	= {}
		self._repo_catalogs		= []

	def catalogs(self, enabled=True):
		"""Lista los catalogos disponibles

		Args:
			enabled (bool): (Opcional) 	**True**: Solo los habilitados,
										**False**: Los deshabilitados,
										**None**: Todos

		Return:
			List: Lista de catalogos

		Example:
			>>> from openerm.OermClient import OermClient
			>>> c = OermClient("samples/openermcfg.yaml")
			>>> c.catalogs(enabled=None)
			>>> print("Catalogos disponibles: {0}".format(c.catalogs(enabled=None)))
			Catalogos disponibles: {'sql-test': {'enabled': False, 'name': 'Ejemplo catalogo SQL', 'type': 'sql'}, '
			local-test': {'enabled': True, 'name': 'Ejemplo catalogo local', 'type': 'path', 'urls':
			[{'Prueba1': 'D:\\pm\\data\\git.repo\\openerm\\samples\\repo'},
			{'Prueba2': 'D:\\pm\\data\\git.repo\\openerm\\samples\\otro'}]}}

		"""
		return {k: self._catalogs[k] for k, v in self._catalogs.items() if enabled is None or v["enabled"] == enabled}

	def current_catalog(self):
		return self._current_catalog

	def repos(self):
		"""Lista los repositorios disponibles para conectarse

		Return:
			List: Lista de repositorios

		Example:
			>>> from openerm.OermClient import OermClient
			>>> c = OermClient("samples/openermcfg.yaml")
			>>> c.open_catalog("local-test")
			>>> print("Repositorios disponibles: {0}".format(c.repos()))
			Repositorios disponibles: {'Prueba2': 'D:\\pm\\data\\git.repo\\openerm\\samples\\otro\\repo.db',
			'Prueba1': 'D:\\pm\\data\\git.repo\\openerm\\samples\\repo\\repo.db'}

		"""
		return self._repo_catalogs

	def open_repo(self, repo):
		"""Abre un repositorio

		Args:
			repo (string): Nombre del repositorio a abrir

		Raise:
			ValueError: Si el repositorio no existe en el catalgo abierto
		"""
		if repo not in self._repo_catalogs:
			raise ValueError(_("El repositorio {0} no existe").format(repo))
		else:
			self._current_repo = {repo: self._repo_catalogs[repo]}

	def reports(self, system=None):
		"""Retorna la lista completa de reportes del repositorio activo

		Returns:
			list

		Ejemplo:
			>>> from openerm.OermClient import OermClient
			>>> c = OermClient("samples/openermcfg.yaml")
			>>> c.open_catalog("local-test")
			>>> c.open_repo("Prueba1")
			>>> print(c.reports())
		"""
		(k, dbname), = self._current_repo.items()
		conn = sqlite3.connect(dbname)
		c = conn.cursor()
		c.execute("SELECT report_id, report_name FROM report")
		r = c.fetchall()
		c.close()
		conn.close()
		return r

	def systems(self):
		"""Retorna la lista completa de sistemas del repositorio activo

		Returns:
			list

		Ejemplo:
			>>> from openerm.OermClient import OermClient
			>>> c = OermClient("samples/openermcfg.yaml")
			>>> c.open_catalog("local-test")
			>>> c.open_repo("Prueba1")
			>>> print(c.systems())
		"""
		dbname, = self._current_repo.values()
		conn = sqlite3.connect(dbname)
		c = conn.cursor()
		c.execute("SELECT system_id, system_name FROM system")
		r = c.fetchall()
		c.close()
		conn.close()
		return r

	def query(self, reporte=None, sistema=None, aplicacion=None, departamento=None, fecha=None, limit=None, returntype="list"):
		"""Consulta básica para buscar un reporte en los repositorios del catalogo.
		La busqueda se hace por cualquier de los atributos básicos de un reporte, y
		se puede hacer búsquedas parciales tipo LIKE en sql

		Args:
			report (string): Nombre del reporte
			sistema (string): Nombre del sistema
			aplicacion (string): Nombre de la aplicación
			departamento (string): Nombre del departamento
			fecha (string): Fecha de emsión del reporte
			limit (int): cantidad máxima de resultados
			returntype (string): Tipo de retorno

		Returns:
			list/string

		Ejemplo:
			>>> from openerm.OermClient import OermClient
			>>> c = OermClient("samples/openermcfg.yaml")
			>>> c.open_catalog("local-test")
			>>> c.open_repo("Prueba1")
			>>> resultados = c.query(reporte="Carta", returntype="tablestr")
			>>> print(resultados)
			+----------------------------------------------------+----------+----------------+-----------+--------------+-----------+---------------------+
			| Nombre                                             |    Fecha | Departamento   | Sistema   | Aplicación   |   Páginas | Path                |
			|----------------------------------------------------+----------+----------------+-----------+--------------+-----------+---------------------|
			| R8101614 - Cartas fianza activas por moneda y clas | 20160923 | n/a            | n/a       | n/a          |         1 | test1\database.oerm |
			| R8101614 - Cartas fianza activas por moneda y clas | 20160923 | n/a            | n/a       | n/a          |        20 | test1\database.oerm |
			| R8101611 - Cartas fianza requeridas por funcionari | 20160923 | n/a            | n/a       | n/a          |         1 | test1\database.oerm |
			+----------------------------------------------------+----------+----------------+-----------+--------------+-----------+---------------------+
		"""

		lista = []
		SQL = """
		Select	distinct
				report.report_name,
				date.date,
				department.department_name,
				system.system_name,
				application.application_name,
				reports.pages,
				databases.path
		From
				reports Inner Join
				department On reports.department_id = department.department_id Inner Join
				date On reports.date_id = date.date_id Inner Join
				report On reports.report_id = report.report_id Inner Join
				application On reports.aplicacion_id = application.application_id Inner Join
				system On reports.system_id = system.system_id Inner Join
				databases On reports.database_id = databases.database_id
		where	1 = 1
				and report.report_name like ?
				and date.date like ?
		"""

		reporte = '%' if reporte is None else '%' + reporte + '%'
		sistema = '%' if sistema is None else '%' + sistema + '%'
		aplicacion = '%' if aplicacion is None else '%' + aplicacion + '%'
		departamento = '%' if departamento is None else '%' + departamento + '%'
		fecha = '%' if fecha is None else '%' + fecha + '%'

		for dbname in self._current_repo.values():
			conn = sqlite3.connect(dbname)
			c = conn.cursor()
			c.execute(SQL, (reporte, fecha, ))
			lista.extend(c.fetchall())

		c.close()
		conn.close()

		if returntype == "list":
			return lista

		if returntype == "tablestr":
			tablestr = tabulate(
							tabular_data		= lista,
							headers				= ["Nombre", "Fecha", "Departamento", "Sistema", "Aplicación", "Páginas", "Path" ],
							floatfmt			= "8.2f",
							tablefmt			= "psql",
							numalign			= "right",
							stralign			= "left",
							override_cols_fmt	= [None, None, None, None, None, ",.0f", None ]
			)
			return tablestr

		return lista

	# def attributes(self, attribute):
	# 	"""Retorna la lista de atributos de los reportes del repositorio"""
	# 	return []

	# def find_indexes(self, indexname):
	# 	"""Retorna la lista de indices que coincidan por indexname"""
	# 	return []

	# def search_for_indexes(self, indexnames, value):
	# 	"""Retorna la lista de indices que coincidan por indexname"""
	# 	return []

if __name__ == "__main__":

	config = """
	catalogs:
		local-test:
			name: Ejemplo catalogo local
			type: path
			enabled: True
			urls:
				- Prueba1: D:\\pm\\data\\git.repo\\openerm\\samples\\repo
				- Prueba2: D:\\pm\\data\\git.repo\\openerm\\samples\\otro
		sql-test:
			name: Ejemplo catalogo SQL
			type: sql
			enabled: false
	"""
	c = OermClient()
	c._load_config(config)

	print("Catalogos disponibles: {0}".format(c.catalogs(enabled=None)))

	c.open_catalog("local-test")

	print("Repositorios disponibles: {0}".format(c.repos()))

	try:
		c.open_repo("Prueba1")
	except ValueError as e:
		print(e)

	print(c._current_repo)
	# print(c.reports())
	# print(c.systems())

	resultados = c.query(reporte="Cartas", returntype="tablestr")
	print(resultados)
	resultados = c.query(fecha="0926", returntype="tablestr")
	print(resultados)
	resultados = c.query(reporte="Carta", returntype="tablestr")
	print(resultados)
