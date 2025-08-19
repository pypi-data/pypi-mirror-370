_A='Plugins must implement the method'
from abc import ABC,abstractmethod
class ProcessorInterface(ABC):
	@property
	@abstractmethod
	def _components(self):0
	def __init__(A,path,name='',encoding='',ignore=None,curve_parser=None,reader_options=None):raise NotImplementedError(_A)
	def class_info(A):raise NotImplementedError(_A)
	def info(A):B={'reader':A.__class__.__name__,'reader_category':A.category,'name':A.name};B.update(A.class_info());return B