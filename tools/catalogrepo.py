#!python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# catalogrepo.py
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
catalogrepo
===========

Esta herramienta realiza la indización o catálogo de los reportes
contenidos en un repositorio **OpenErm**. Un repositorio no es más
que una carpeta que contiene un conjunto de subcarpetas, y en estas
un **Database** Oerm

"""

__author__		= "Patricio Moracho <pmoracho@gmail.com>"
__appname__		= "catalogrepo"
__appdesc__		= "Catalogación de un repositorio OpenErm"
__license__		= 'GPL v3'
__copyright__	= "(c) 2016, %s" % (__author__)
__version__		= "0.9"
__date__		= "2016/09/14"


try:
	import sys
	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	def _my_gettext(s):
		"""Traducir algunas cadenas de argparse."""
		current_dict = {'usage: ': 'uso: ',
						'optional arguments': 'argumentos opcionales',
						'show this help message and exit': 'mostrar esta ayuda y salir',
						'positional arguments': 'argumentos posicionales',
						'the following arguments are required: %s': 'los siguientes argumentos son requeridos: %s'}

		if s in current_dict:
			return current_dict[s]
		return s

	gettext.gettext = _my_gettext

	import argparse
	# import time
	import os
	import sqlite3

	sys.path.append('.')
	sys.path.append('..')

	from openerm.Database import Database
	from openerm.tabulate import *
	from openerm.Utils import *

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


def init_argparse():
	"""Inicializar parametros del programa."""
	cmdparser = argparse.ArgumentParser(prog=__appname__,
										description="%s\n%s\n" % (__appdesc__, __copyright__),
										epilog="",
										add_help=True,
										formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)
	)

	opciones = {	"inputpath": {
								"type": str,
								"action": "store",
								"help": _("Path a procesar")
					}
			}

	for key, val in opciones.items():
		args = key.split()
		kwargs = {}
		kwargs.update(val)
		cmdparser.add_argument(*args, **kwargs)

	return cmdparser


def procces_tree(path, update=False):
	"""Procesa el path de un repositorio de datbases Oerm

	Args:
		path (string): Carpeta principal del repositorio
		update (bool): (Opcional) Se actualiza o regenera completamente el catalogo

	"""
	dbname = os.path.join(path, 'catalog.db')
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
		for report in d.Reports():

			print("{0}: {1}".format(report.nombre, reportid.get(report.nombre)))

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

if __name__ == "__main__":

	cmdparser = init_argparse()
	try:
		args = cmdparser.parse_args()
	except IOError as msg:
		args.error(str(msg))

	inputpath = args.inputpath
	if inputpath:
		procces_tree(inputpath)
