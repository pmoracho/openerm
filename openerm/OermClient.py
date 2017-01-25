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
	from openerm.Utils import file_accessible, AutoNum, filesInPath
	from openerm.Database import Database


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
		dbname, = self._current_repo.values()
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

	def catalog_create(self, catalogdict):
		"""Crear un catálogo (lógico) de repositorios Oerm.

		Args:
			catalogdict (dict): Configuración del catálogo

		Raise:
			ValueError si el catalogo <id> ya existe

		Ejemplo:
			>>> from openerm.OermClient import OermClient
			>>> c = OermClient("samples/openermcfg.yaml")
			>>> catalog_config = {"catalogo1": { "name": "Ejemplo catalogo local", "type": "path", "enabled": True, "url": "c:/oerm/"}}
			>>> c.catalog_create(catalog_config)

		"""

		if id in self._catalogs:
			raise ValueError(_("El catalogo {0} ya está definido en la instancia actual del cliente Oerm").format(id))
		else:
			self.config["catalogs"].update(catalogdict)
			self._flush()

	def _flush(self):
		with open(self.configfile, 'w') as outfile:
			yaml.dump(self.config, outfile, default_flow_style=True)

	def add_repo(self, catalog_id, path, update=False):

		"""Procesa el path de un repositorio de datbases Oerm y genera el
		repo.db (sqlite). Basicamente cataloga cada database y genera una
		base sqlite (repo.db) en el directorio root del repositorio.

		Args:
			catalog_id (string): Id del catálogo al cual se agregará este repositorio
			path (string): Carpeta principal del repositorio
			update (bool): (Opcional) Se actualiza o regenera completamente el catalogo

		"""
		dbname = os.path.join(path, 'repo.db')
		if file_accessible(dbname, "r"):
			os.remove(dbname)

		conn = sqlite3.connect(dbname)
		# conn.text_factory = lambda x: repr(x)
		c = conn.cursor()
		c.execute("CREATE TABLE databases (database_id int, path text)")

		c.execute("CREATE TABLE date		(date_id INTEGER PRIMARY KEY ASC, date text)")
		c.execute("CREATE TABLE system		(system_id INTEGER PRIMARY KEY ASC, system_name text)")
		c.execute("CREATE TABLE application (application_id INTEGER PRIMARY KEY ASC, application_name text)")
		c.execute("CREATE TABLE department	(department_id INTEGER PRIMARY KEY ASC, department_name text)")
		c.execute("CREATE TABLE report		(report_id INTEGER PRIMARY KEY ASC, report_name text)")

		c.execute("CREATE TABLE reports	(database_id int, report_id int, aplicacion_id int, date_id int, system_id, department_id int, pages int)")
		# c.execute("CREATE TABLE reports (database_id int, report_id text, report_name text, aplicacion text, fecha text, sistema text, departamento text, pages int)")

		databases		= []
		reports_list	= []

		reportid 	= AutoNum()
		dateid		= AutoNum()
		systemid	= AutoNum()
		appid		= AutoNum()
		deptid		= AutoNum()

		for i, f in enumerate(filesInPath(path, "*.oerm"), 1):
			databases.append((i, f))
			d = Database(os.path.join(path, f), mode="rb")
			print(os.path.join(path, f))
			for report in d.reports():

				# print("{0}: {1}".format(report.nombre, reportid.get(report.nombre)))

				elemento = (i,
							reportid.get(report.nombre),
							appid.get(report.aplicacion),
							dateid.get(report.fecha),
							systemid.get(report.sistema),
							deptid.get(report.departamento),
							report.total_pages
						)
				reports_list.append(elemento)

		c.executemany("INSERT INTO date (date, date_id) VALUES (?,?)", dateid.list())
		c.executemany("INSERT INTO system (system_name, system_id) VALUES (?,?)", systemid.list())
		c.executemany("INSERT INTO application (application_name, application_id) VALUES (?,?)", appid.list())
		c.executemany("INSERT INTO department (department_name, department_id) VALUES (?,?)", deptid.list())
		c.executemany("INSERT INTO report (report_name, report_id) VALUES (?,?)", reportid.list())
		c.executemany("INSERT INTO databases (database_id, path) VALUES (?,?)", databases)
		c.executemany("INSERT INTO reports (database_id, report_id, aplicacion_id, date_id, system_id, department_id, pages) VALUES (?,?,?,?,?,?,?)", reports_list)

		conn.commit()
		conn.close()

		d = self.config["catalogs"].get(catalog_id)
		if "url" not in d:
			d["url"] = [path]
		else:
			d["url"].append(path)

		self._flush()


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
