# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>

Index.py

This program is free software; you can redistribute it and/or
modify it under the terms of version 3 of the GNU General Public License
as published by the Free Software Foundation. A copy of this license should
be included in the file GPL-3.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
GNU Library General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

try:

	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import struct
	import sys

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class Index(object):

	def __init__(self, oermdb_file):

		self.oermdb_file			= oermdb_file
		self.current_report_id		= 0
		self.reports				= {}
		self.reportidx_file			= "{0}.ridx".format(self.oermdb_file)
		self.containeridx_file		= "{0}.cidx".format(self.oermdb_file)
		self.metadata_objects 		= 0
		self.container_objects 		= 0

	def get_report(self, reporte):
		"""Obtiene el id de un reporte en el índice"""
		for k,r in self.reports.items():
			if r[0] == reporte[0:50]:
				return k
		return None

	def add_report(self, reporte, report_offset, pages_in_container):

		self.current_report_id		+= 1
		default						= (reporte[0:50], report_offset, pages_in_container, 0, [])
		self.reports[self.current_report_id] = default
		return self.current_report_id

	def add_container(self, reporte_id, container_offset):

		self.reports[reporte_id][4].append(container_offset)

	def write(self):

		# Salvar offset de los bloques de metadatos del reporte
		struct_fmt			= ">L50sQHQ"
		container_offsset 	= 0
		with open(self.reportidx_file, mode="wb+") as file:
			for key,report in self.reports.items():
				data		= struct.pack(	struct_fmt,
											key,									# ID númerico del reporte en la base 1..n
											report[0].encode("utf-8", "replace"),	# Nombre del reporte
											report[1],								# Offset del bloque de metadatos del reporte en el contenedor
											report[2],								# Cantidad de páginas esperadas en el contenedor de páginas
											container_offsset						# Offet al primer contenedores de página del reporte
		  								)

				container_offsset += len(report[4]) * 12
				file.write(data)
				self.metadata_objects = +1

		# Salvar offest a los contenedores de páginas
		struct_fmt	= ">LQ"
		with open(self.containeridx_file, mode="wb+") as file:
			for key, report in self.reports.items():
				for group_offset in report[4]:
					data		= struct.pack(	struct_fmt,
												key,								# iD númerico del reporte en la base 1..n
												group_offset						# Offet al contenedor de páginas
											)
					file.write(data)
					self.container_objects = +1

	def read(self):

		# Recupero offsets a los metadatos
		struct_fmt		= ">L50sQHQ"
		longitud_bloque	= struct.calcsize(struct_fmt)
		struct_unpack	= struct.Struct(struct_fmt).unpack_from

		with open(self.reportidx_file, mode="rb") as file:
			while True:
				data	= file.read(longitud_bloque)
				if not data:
					break
				fields									= struct_unpack(data)
				default									= (fields[1].decode("utf-8").strip("\0"), fields[2], fields[3], fields[4], [])
				self.current_report_id					= fields[0]
				self.reports[self.current_report_id]	= default
				self.metadata_objects					+= 1


		# Recupero offsets a los contenedores
		struct_fmt		= ">LQ"
		longitud_bloque	= struct.calcsize(struct_fmt)
		struct_unpack	= struct.Struct(struct_fmt).unpack_from

		with open(self.containeridx_file, mode="rb") as file:
			while True:
				data	= file.read(longitud_bloque)
				if not data:
					break
				fields	= struct_unpack(data)
				id		= fields[0]
				self.reports[id][4].append(fields[1])
				self.container_objects += 1

	def __str__( self ) :
		print(self.reports)
