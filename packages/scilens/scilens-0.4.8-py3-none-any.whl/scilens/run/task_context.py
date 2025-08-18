import os
from scilens.config.models import AppConfig
class TaskContext:
	working_dir:str;origin_working_dir:str;config:AppConfig;config_file:str|None=None
	def __init__(A,working_dir,origin_working_dir,config,config_file):
		E='working_dir must be an absolute path.';D='working_dir does not exist.';C=origin_working_dir;B=working_dir
		if not os.path.isdir(B):raise Exception(D)
		if not os.path.isabs(B):raise Exception(E)
		if not os.path.isdir(C):raise Exception(D)
		if not os.path.isabs(C):raise Exception(E)
		A.config=config;A.config_file=config_file;A.working_dir=B;A.origin_working_dir=C;A.task_name=''
		if len(B)>len(C):A.task_name=B.replace(C,'')