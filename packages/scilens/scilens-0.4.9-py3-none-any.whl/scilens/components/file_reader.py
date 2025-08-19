_A=None
import logging,importlib,os
from scilens.config.models import FileReaderConfig
from scilens.config.models.readers import ReadersConfig
from scilens.readers.reader_manager import ReaderManager
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.exceptions import NoReaderFound
class FileReader:
	def __init__(A,absolute_working_dir,config,readers_config,config_alternate_path=_A):A.path=absolute_working_dir;A.config_alternate_path=config_alternate_path;A.reader_mgmr=ReaderManager();A.config=config;A.readers_config=readers_config
	def _get_custom_parser(D,config_parser):
		E=config_parser
		if not E:return
		A,H=E.split('::');B=_A;I=[A,f"{D.path}/{A}",f"{D.config_alternate_path}/{A}"]
		for C in I:
			if os.path.exists(C):B=C;break
		if not B:raise Exception(f"Custom curve parser not found: {A}")
		J=C.split('/')[-1].replace('.py','');F=importlib.util.spec_from_file_location(J,B);G=importlib.util.module_from_spec(F);F.loader.exec_module(G);return getattr(G,H)
	def read(A,path):
		logging.info(f"Reading file: {path}");D=_A;B=A.config.custom_curve_parser
		if B:
			if isinstance(B,str):D=A._get_custom_parser(B)
		try:C,E=A.reader_mgmr.get_reader_from_file(path,config=A.config,readers_config=A.readers_config,curve_parser=D);C.read(E)
		except NoReaderFound:
			if A.config.extension_unknown_ignore:C=_A
			else:raise Exception(f"No reader found")
		return C