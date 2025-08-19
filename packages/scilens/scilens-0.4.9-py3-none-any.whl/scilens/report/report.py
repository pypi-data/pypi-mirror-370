_A='html'
import logging,json,os
from pydantic import BaseModel
from scilens.config.models import ReportConfig
from scilens.utils.file import file_remove,json_write,text_write,yaml_write
from scilens.utils.php import dict_to_php_array
from scilens.report.html_report import HtmlReport
class ReportProcessResults(BaseModel):files_created:list[str]=[]
class Report:
	def __init__(B,working_dir,alt_config_dirs,config,task_name):A=config;B.path=working_dir;B.alt_config_dirs=alt_config_dirs;B.config=A;B.task_name=task_name;B.extensions={'txt':A.output.export_txt,'json':A.output.export_json,'yaml':A.output.export_yaml,_A:A.output.export_html,'py':A.output.export_py,'js':A.output.export_js,'ts':A.output.export_ts,'php':A.output.export_php}
	def _get_file(A,ext):return os.path.join(A.path,f"{A.config.output.filename}.{ext}")
	def process(B,data,processor=None):
		I=False;D=data;E=ReportProcessResults();logging.info(f"Processing report");J=B.config;F=B.extensions;logging.info(f"Cleaning reports")
		for A in F:file_remove(B._get_file(A))
		G=I
		for(A,K)in F.items():
			if K:
				logging.info(f"Creating report {A}");G=True;C=B._get_file(A);H=True
				if A=='txt':text_write(C,str(D))
				elif A=='json':json_write(C,D)
				elif A=='yaml':yaml_write(C,D)
				elif A=='py':text_write(C,'DATA = '+format(D))
				elif A in['js','ts']:text_write(C,'export default '+json.dumps(D))
				elif A=='php':text_write(C,'<?php\nreturn '+dict_to_php_array(D)+';\n')
				elif A==_A:text_write(C,HtmlReport(B.config,B.alt_config_dirs,B.path).process(processor,D,B.task_name),encoding='utf-8')
				else:H=I;logging.error(f"Extension {A} not implemented")
				if H:E.files_created.append(C)
		if J.output.export_html:logging.info(f"Report generated at file://{B._get_file(_A)}")
		if not G:logging.warning(f"No report to process")
		return E