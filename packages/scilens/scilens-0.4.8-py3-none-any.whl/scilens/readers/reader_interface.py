_A='Plugins must implement the method'
from abc import ABC,abstractmethod
from pydantic import BaseModel
class ReaderOrigin(BaseModel):type:str;path:str;short_name:str=''
class ReaderInterface(ABC):
	@property
	@abstractmethod
	def category(self):0
	def __init__(A,origin,name='',encoding='',curve_parser=None):A.origin=origin;A.name=name;A.encoding=encoding or'utf-8';A.curve_parser=curve_parser;A.read_error=None;A.read_data={};A.reader_info={}
	def read(A,reader_options=None):raise NotImplementedError(_A)
	def compare(A,reader,param_is_ref=True):raise NotImplementedError(_A)
	def get_raw_lines(A,line_nb,pre=0,post=0):raise NotImplementedError(_A)
	def class_info(A):raise NotImplementedError(_A)
	def close(A):0
	def info(A):B={'reader':A.__class__.__name__,'reader_info':A.reader_info,'name':A.name,'origin':A.origin.dict(),'encoding':A.encoding,'read_error':A.read_error,'read_data':A.read_data};B.update(A.class_info());return B