import logging,os
from mimetypes import MimeTypes
from scilens.app import pkg_name,pkg_version,pkg_homepage,product_name,powered_by
from scilens.config.models import ReportConfig
from scilens.report.template import template_render_infolder
from scilens.report.assets import get_image_base64,get_image_base64_local,get_logo_image_src
from scilens.utils.time_tracker import TimeTracker
class HtmlReport:
	def __init__(A,config,alt_config_dirs,working_dir=None):A.config=config;A.alt_config_dirs=alt_config_dirs;A.working_dir=working_dir
	def process(A,processor,data,task_name):
		I='meta';H='date';logging.info(f"Processing html report");J=TimeTracker();B=J.get_data()['start']
		if A.config.logo and A.config.logo_file:raise ValueError('logo and logo_file are exclusive.')
		K=A.config.logo;C=None
		if A.config.logo_file:
			D=A.config.logo_file
			if os.path.isabs(D):
				C=D
				if not os.path.isfile(E):raise FileNotFoundError(f"Logo file '{A.config.logo_file}' not found.")
			else:
				F=list(set([A.working_dir]+A.alt_config_dirs))
				for L in F:
					E=os.path.join(L,D)
					if os.path.isfile(E):C=E;break
				if not C:raise FileNotFoundError(f"Logo file '{A.config.logo_file}' not found in {F}.")
		M=A.config.title if A.config.title else A.config.title_prefix+' '+task_name;N={'app_name':product_name,'app_version':pkg_version,'app_homepage':pkg_homepage,'app_copyright':f"© {B[H][:4]} {powered_by['name']}. All rights reserved",'app_powered_by':powered_by,'execution_utc_datetime':B['datetime'],'execution_utc_date':B[H],'execution_utc_time':B['time'],'execution_dir':A.working_dir,'title':M,'description':A.config.description,'image':K or get_logo_image_src(C),'config':A.config.html,'config_json':A.config.html.model_dump_json()};G=None
		if A.config.debug:G=A.config.model_dump_json(indent=4)
		return template_render_infolder('index.html',{I:N,'task':data.get(I),'data':{'files':data.get('processor_results')},'debug':G})