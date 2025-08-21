import unittest


class AbstractTestUtil(unittest.TestCase):
	overrideTestUtil=None
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		logger=type('test',(),{})()
		logger.exception=logger.error=logger.warning=logger.info=logger.debug=print
		self.logger=logger
