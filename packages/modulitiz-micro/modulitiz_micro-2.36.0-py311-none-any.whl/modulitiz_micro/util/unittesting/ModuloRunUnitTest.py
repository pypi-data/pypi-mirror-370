import os
import pkgutil
import unittest


class ModuloRunUnitTest(object):
	
	@classmethod
	def startTests(cls,currentFilePath:str):
		suite=cls.__createTestSuite(currentFilePath)
		unittest.TextTestRunner(verbosity=2).run(suite)
	
	@staticmethod
	def __createTestSuite(currentFilePath:str)->unittest.TestSuite:
		paths = [x[0] for x in os.walk(os.path.dirname(currentFilePath))]
		testLoader=unittest.TestLoader()
		suite=unittest.TestSuite()
		for modFinder, modName, _isPkg in pkgutil.walk_packages(paths):
			spec=modFinder.find_spec(modName)
			loader=spec.loader
			module=loader.load_module(modName)
			# carico ogni test presente in un modulo
			for tests in testLoader.loadTestsFromModule(module):
				suite.addTests(tests)
		return suite
