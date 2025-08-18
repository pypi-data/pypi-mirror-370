_A=None
import os,sys
from importlib.metadata import entry_points
from scilens.readers.exceptions import NoReaderFound
from scilens.readers.reader_interface import ReaderOrigin
from scilens.config.models import FileReaderConfig
from scilens.config.models.readers import ReadersConfig
def extension_format(extension):
	A=extension
	if A.startswith('.'):A=A[1:]
	return A.upper()
from scilens.readers.reader_txt import ReaderTxt
from scilens.readers.reader_csv import ReaderCsv
from scilens.readers.reader_txt_fixed_cols import ReaderTxtFixedCols
BUILTIN_PLUGINS=[ReaderTxt,ReaderCsv,ReaderTxtFixedCols]
LIB_PLUGINS_ENTRY_POINT='scilens.reader_plugins'
class ReaderManager:
	def __init__(A):
		A.plugins=[]+BUILTIN_PLUGINS;B=entry_points(group=LIB_PLUGINS_ENTRY_POINT)if sys.version_info.minor>=12 else entry_points().get(LIB_PLUGINS_ENTRY_POINT,[])
		for C in B:A.plugins+=C.load()()
	def _get_plugin_names(A):return[A.__name__ for A in A.plugins]
	def _get_plugin_info(A):return[{'class':A.__name__,'configuration_type_code':A.configuration_type_code}for A in A.plugins]
	def __str__(A):return f"plugins: {A._get_plugin_names()}"
	def _get_reader_from_extension(B,extension):
		for A in B.plugins:
			if extension_format(extension)in A.extensions:return A
	def _get_reader_from_configuration_type_code(B,code):
		for A in B.plugins:
			if code==A.configuration_type_code:return A
	def get_reader_from_file(F,path,name='',config=_A,readers_config=_A,curve_parser=_A):
		I=curve_parser;G=path;C=readers_config;A=config;J=ReaderOrigin(type='file',path=G,short_name=os.path.basename(G));K=A.encoding if A else'utf-8';Q,D=os.path.splitext(G);D=extension_format(D)
		if A and A.extension_readers_catalog:
			for(M,L)in A.extension_readers_catalog.items():
				if extension_format(M)==D:
					if not C.catalog or L not in C.catalog.keys():raise NoReaderFound(f"Reader config not found for {D}")
					H=C.catalog[L];B=F._get_reader_from_configuration_type_code(H.type)
					if not B:raise Exception(f"Reader not found for contiguration type code {H.type}")
					N=H.parameters;return B(J,name=name,encoding=K,curve_parser=I),N
		if A and A.extension_mapping:
			for(O,P)in A.extension_mapping.items():
				if extension_format(O)==D:D=extension_format(P);break
		B=F._get_reader_from_extension(D)
		if not B and A and A.extension_fallback:B=F._get_reader_from_extension(A.extension_fallback)
		if not B:raise NoReaderFound(f"Reader cound not be derived")
		E=_A
		if B.__name__=='ReaderTxt':E=C.txt
		elif B.__name__=='ReaderCsv':E=C.csv
		elif B.__name__=='ReaderTxtFixedCols':E=C.txt_fixed_cols
		elif B.__name__=='ReaderNetcdf':E=C.netcdf
		return B(J,name=name,encoding=K,curve_parser=I),E