#!python

import unittest
import sys
import time

sys.path.append('.')
sys.path.append('..')

from openerm.tabulate import *

class CustomTestRunner:

	def __init__(self, stream=sys.stderr):
		self.stream = stream
		self.lista	= []

	def writeUpdate(self, message):
		self.stream.write(message)

	def run(self, test):
		"Run the given test case or test suite."

		result = _XmlTestResult(self)
		startTime = time.time()

		test(result)

		stopTime = time.time()
		timeTaken = float(stopTime - startTime)

		result.addErrorsToList()
		run = result.testsRun
		v = (timeTaken)
		self.lista.append(v)

		return result

class _XmlTestResult(unittest.TestResult):
	"""A test result class that can print

	CustomTestRunner.
	"""

	def __init__(self, runner):
		unittest.TestResult.__init__(self)
		self.runner = runner

		self.startTime = 0

		self.current_test_id = 0
		self.resultados = []

	def startTest(self, test):
		self.startTime = time.time()
		unittest.TestResult.startTest(self, test)

	def addSuccess(self, test):

		stopTime = time.time()
		timeTaken = float(stopTime - self.startTime)

		unittest.TestResult.addSuccess(self, test)

		self.current_test_id += 1
		nombre_test = test.id()[test.id().rfind(".")+1:]
		v = (self.current_test_id, nombre_test, test.shortDescription(), timeTaken, "Ok", None)
		self.resultados.append(v)

	# def addError(self, test, err):
	#	stopTime = time.time()
	#	timeTaken = float(stopTime - self.startTime)

	#	unittest.TestResult.addError(self, test, err)

	#	self.current_test_id += 1
	#	v = (self.current_test_id, test.id(), test.shortDescription(), timeTaken, "Error")
	#	self.resultados.append(v)

	# def addFailure(self, test, err):
	#	stopTime = time.time()
	#	timeTaken = float(stopTime - self.startTime)

	#	unittest.TestResult.addFailure(self, test, err)

	#	self.current_test_id += 1
	#	v = (self.current_test_id, test.id(), test.shortDescription(), timeTaken, "Failure")
	#	self.resultados.append(v)


	def addErrorsToList(self):
		self.addErrorToList('Error', self.errors)
		self.addErrorToList('Failure', self.failures)
		pass

	def addErrorToList(self, flavor, errors):

		for test, err in errors:
			self.current_test_id += 1
			nombre_test = test.id()[test.id().rfind(".")+1:]
			v = (self.current_test_id, nombre_test, test.shortDescription(), 0, flavor, err)
			self.resultados.append(v)

	def printErrorList(self, flavor, errors):

		for test, err in errors:
			self.runner.writeUpdate('<%s testcase="%s">\n' % (flavor, test.shortDescription()))
			self.runner.writeUpdate('<' + '![CDATA[')
			self.runner.writeUpdate("%s" % err)
			self.runner.writeUpdate(']]' + '>')
			self.runner.writeUpdate("</%s>\n" % flavor)


if __name__ == '__main__':

	testRunner	= CustomTestRunner()

	if len(sys.argv) < 1:
		test_pattern = sys.argv[1]
		testsuite	= unittest.TestLoader().discover(start_dir='.', pattern=test_patter)
	else:
		testsuite	= unittest.TestLoader().discover(start_dir='.')

	results		= testRunner.run(testsuite)

	tablestr = tabulate(
		tabular_data		= [(r[0],r[1], r[2], r[3], r[4]) for r in results.resultados],
					headers				= ["#", "Id", "Test", "Tiempo (segs)", "Status"],
					floatfmt			= "8.2f",
					tablefmt			= "psql",
					numalign			= "right",
					stralign			= "left"
	)
	print("")
	print("Estatus de los tests:")
	print("=====================")
	print("")
	print(tablestr)
	print("")

	errores = [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in results.resultados if r[5]]
	lista	= []
	for error in [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in results.resultados if r[5]]:
		lista.append((error[1], None))
		for e in error[5].split("\n"):
			lista.append((None, e))

	if lista:

		tablestr = tabulate(
					tabular_data		= lista,
					headers				= ["Id", "Detalle"],
					floatfmt			= "8.2f",
					tablefmt			= "psql",
					numalign			= "right",
					stralign			= "left"
		)
		print("")
		print("Errores detectados:")
		print("===================")
		print("")
		print(tablestr)
		print("")