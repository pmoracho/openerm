# -*- coding: utf-8 -*-

# Copyright (c) 2014 Patricio Moracho <pmoracho@gmail.com>
#
# Config.py
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
LoadProcess
===========

Esta clase define un objeto de procesamiento y carga de spool

"""


try:

	import gettext
	from gettext import gettext as _
	gettext.textdomain('openerm')

	import sys
	import os
	import time
	from progressbar import Bar, ETA, FileTransferSpeed, FormatLabel, ProgressBar

	sys.path.append('.')
	sys.path.append('..')

	from openerm.Block import Block
	from openerm.Database import Database
	from openerm.ReportMatcher import ReportMatcher
	from openerm.SpoolHostReprint import SpoolHostReprint
	from openerm.SpoolFixedRecordLength import SpoolFixedRecordLength
	from openerm.tabulate import tabulate
	from openerm.Config import LoadConfig

except ImportError as err:
	modulename = err.args[0].partition("'")[-1].rpartition("'")[0]
	print(_("No fue posible importar el modulo: %s") % modulename)
	sys.exit(-1)


class LoadProcess(object):

	def __init__(self, configfile, input_file=None):

		self.config     = LoadConfig(configfile)
		self.input_file = input_file

	def process_file(self, input_file):

		block           = Block(default_compress_level = self.config.compress_level)
		resultados      = []
		self.input_file = input_file
		size_test_file  = os.path.getsize(self.input_file)

		self.spool_types = {
						"fixed": SpoolFixedRecordLength(self.input_file, buffer_size=self.config.buffer_size, encoding=self.config.encoding, newpage_code=self.config.EOP ),
					  	"fcfc":	SpoolHostReprint(self.input_file, buffer_size=self.config.buffer_size, encoding=self.config.encoding )
					  }

		compresiones 	= [e for e in block.compressor.available_types if e[0] == self.config.compress_type]
		encriptados 	= [e for e in block.cipher.available_types if e[0] == self.config.cipher_type]

		mode = "ab"

		r = ReportMatcher(self.config.report_cfg)
		reports = []
		for encriptado in encriptados:
			for compress in compresiones:

				start		= time.time()
				paginas		= 0

				# file_name	= "{0}.{1}.oerm".format(self.config.output_path, slugify("{0}.{1}".format(compress[1], encriptado[1]), "_"))
				file_name	= os.path.join(self.config.output_path, self.config.file_mask + ".oerm")

				db	= Database(	file=file_name,
								mode=mode,
								default_compress_method=compress[0],
								default_compress_level=self.config.compress_level,
								default_encription_method=encriptado[0],
								pages_in_container = self.config.pages_in_group)

				file_size	= os.path.getsize(file_name)
				reportname_anterior = ""

				widgets = [ os.path.basename(self.input_file), ': ',
							FormatLabel('%(value)d bytes de %(max_value)d (%(percentage)0.2f)'),
			   				Bar(marker='#',left='[',right=']'), ' ',
			   				ETA(), ' ',
			   				FileTransferSpeed()]

				p_size = 0
				with ProgressBar(max_value=size_test_file, widgets=widgets) as bar:
					spool = self.spool_types[self.config.file_type]
					with spool as s:
						for page in s:
							p_size += len(page)
							bar.update(p_size)
							data = r.match(page)
							reportname = data[0]

							if reportname not in reports:
								reports.append(reportname)

							if reportname != reportname_anterior:
								rpt_id = db.get_report(reportname)
								if rpt_id:
									db.set_report(reportname)
								else:
									db.add_report(reporte=reportname, sistema=data[1], departamento=data[2], fecha=data[3])
								reportname_anterior = reportname

							paginas = paginas + 1
							db.add_page(page)

					db.close()

				compress_time	= time.time() - start
				compress_size	= os.path.getsize(file_name) - file_size

				resultados.append([
					"[{0}] {1} ({2}p/cont.)".format(compress[0], compress[1], self.config.pages_in_group),
					("" if encriptado[0] == 0 else encriptado[1]),
					float(size_test_file),
					float(compress_size),
					(compress_size/size_test_file)*100,
					paginas/compress_time,
					len(reports)
				])

		tablestr = tabulate(
						tabular_data		= resultados,
						headers				= ["Algoritmo", "Encript.", "Real (bytes)", "Compr. (bytes)", "Ratio", "Compr. Pg/Seg", "Reportes"],
						floatfmt			= "8.2f",
						tablefmt			= "psql",
						numalign			= "right",
						stralign			= "left",
						override_cols_fmt	= [None, None, ",.0f", ",.0f",",.2f", ",.2f", ",.2f"]
		)
		return tablestr
