_A=None
import os
from pydantic import BaseModel
from scilens.utils.file import list_paths_for_file_recursive,text_write
from scilens.report.template import template_render_infolder
from scilens.report.assets import get_logo_image_src
class PathSearchInfo(BaseModel):path:str;dir:str;relative_path:str;relative_dir:str
CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR=os.path.join(CURRENT_DIR,'templates')
class SearchAndIndex:
	def file_discover(F,discover_path,filename):
		D=discover_path;B=filename;E=[]
		for C in list_paths_for_file_recursive(D,B):
			A=C.replace(D,'')
			if A.startswith(os.path.sep):A=A[1:]
			E.append(PathSearchInfo(path=os.path.join(C,B),dir=C,relative_path=os.path.join(A,B),relative_dir=A))
		return E
	def file_list_info_from_origin(D,path_list,origin_path):
		C=[]
		for B in path_list:
			A=B.replace(origin_path,'')
			if A.startswith(os.path.sep):A=A[1:]
			C.append(PathSearchInfo(path=B,dir=os.path.dirname(B),relative_path=A,relative_dir=os.path.dirname(A)))
		return C
	def search_and_create_html_index(A,search_path,search_filename,index_path,title=_A,logo=_A,logo_file=_A):B=A.file_discover(search_path,search_filename);A.create_html_index(B,index_path,title=title,logo=logo,logo_file=logo_file)
	def create_html_index(B,results,index_path,title=_A,logo=_A,logo_file=_A):A=template_render_infolder('index.html',{'meta':{'title':title or'Index','image':logo or get_logo_image_src(logo_file)},'results':results},template_dir=TEMPLATE_DIR);text_write(index_path,A)