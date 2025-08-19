_A=None
import logging,os
from scilens.app import pkg_name
from scilens.utils.file import dir_is_empty,dir_remove,dir_create,copy
from scilens.helpers.search_and_index import SearchAndIndex,PathSearchInfo
class Assets:
	def __init__(A,path,force_clean=False,force_create=False):
		C=path;A.path=C if os.path.isabs(C)else os.path.abspath(C);logging.info(f"Assets directory : {A.path}")
		if os.path.exists(A.path):
			logging.info(f"Assets directory exists")
			if force_clean:logging.info(f"Cleaning assets directory {A.path}");dir_remove(A.path);dir_create(A.path)
			elif not dir_is_empty(A.path):B='Assets directory is not empty';logging.error(B);raise Exception(B)
			else:logging.info(f"Assets directory is empty")
		else:
			logging.info(f"Assets directory does not exists")
			if force_create:logging.info(f"Creating assets directory");dir_create(A.path)
			else:B='Assets directory does not exist';logging.error(B);raise Exception(B)
	def copy(E,paths_infos,items_only=_A):
		B=items_only
		for A in paths_infos:
			C=os.path.join(E.path,A.relative_dir)
			if B:
				for D in B:F=os.path.join(A.dir,D);G=os.path.join(C,D);copy(F,G)
			else:copy(A.dir,C)
	def create_html_index(A,index_path,search_path,search_filename,title=_A,logo=_A,logo_file=_A):SearchAndIndex().search_and_create_html_index(search_path,search_filename,index_path,title=title,logo=logo,logo_file=logo_file)
	def report_get_name(A):return f"{pkg_name}_report.html"
	def report_discover(A,discover_path):return SearchAndIndex().file_discover(discover_path,A.report_get_name())