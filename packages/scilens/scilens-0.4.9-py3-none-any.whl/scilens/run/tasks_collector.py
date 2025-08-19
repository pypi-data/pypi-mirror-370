_A=None
import logging,os
from scilens.app import pkg_name
from scilens.config.load import config_load
from scilens.run.task_context import TaskContext
from scilens.run.run_task import RunTask
from scilens.utils.file import list_paths_at_depth
def configfile_search_in_folder(folder):
	for B in['yml','yaml']:
		A=f"{folder}/{pkg_name}.{B}"
		if os.path.isfile(A):return A
def configfile_search_in_folder_recursive(folder):
	A=folder;B=[];C=configfile_search_in_folder(A)
	if C:return[(A,C)]
	else:
		D=[os.path.join(A,B)for B in os.listdir(A)if os.path.isdir(os.path.join(A,B))]
		for dir in D:B+=configfile_search_in_folder_recursive(dir)
	return B
class TasksCollector:
	def __init__(A,absolute_working_dir,config_filepath=_A,collect_discover=False,collect_depth=_A,tags=_A,processor=_A):
		F=processor;E=collect_discover;D=config_filepath;C=collect_depth;B=absolute_working_dir
		if not os.path.isdir(B):raise Exception('absolute_working_dir does not exist.')
		if not os.path.isabs(B):raise Exception('absolute_working_dir must be an absolute path.')
		A.path=B
		if not bool(D)+E+(bool(C)or C==0)+bool(F)in[0,1]:raise Exception('config_filepath, collect_discover, collect_depth and processor are mutually exclusive.')
		A.config_filepath=D;A.collect_discover=E;A.collect_depth=C;A.processor=F;A.tags=tags
	def process(A,options_path_value):
		F=options_path_value;logging.info(f"Collecting tasks");B=[]
		if A.collect_discover:
			logging.info(f"Collect-discover: Exploring recursively the folder '{A.path}'");H=configfile_search_in_folder_recursive(A.path);logging.info(f"Collect-discover: Number of config files found: {len(H)}");logging.info(f"Loading configurations")
			for(K,I)in H:E=config_load(I,F);C=TaskContext(config=E,config_file=I,working_dir=K,origin_working_dir=A.path);B.append(RunTask(C))
		elif A.processor:E=config_load({'processor':A.processor},F);C=TaskContext(config=E,config_file=_A,working_dir=A.path,origin_working_dir=A.path);B.append(RunTask(C))
		else:
			D=_A
			if A.config_filepath:
				if not os.path.isfile(A.config_filepath):raise Exception(f"Config file '{A.config_filepath}' not found.")
				else:D=os.path.abspath(A.config_filepath)
			else:
				D=configfile_search_in_folder(A.path)
				if D:logging.info(f"Config file found at '{D}'")
				else:raise Exception(f"Config file not found in '{A.path}'")
			E=config_load(D,F)
			if A.collect_depth is not _A:
				logging.info(f"Collecting tasks at depth: {A.collect_depth}");J=list_paths_at_depth(A.path,A.collect_depth);logging.info(f"Number of dirs found: {len(J)}")
				for dir in J:
					G=configfile_search_in_folder(dir)
					if G:L=config_load(D,F,config_override=G);C=TaskContext(config=L,config_file=G,working_dir=dir,origin_working_dir=A.path)
					else:C=TaskContext(config=E,config_file=D,working_dir=dir,origin_working_dir=A.path)
					B.append(RunTask(C))
			else:C=TaskContext(config=E,config_file=D,working_dir=A.path,origin_working_dir=A.path);B.append(RunTask(C))
		if A.tags:logging.info(f"Filtering tasks with tags: {A.tags}");B=[B for B in B if any(A in(B.context.config.tags or[])for A in A.tags)]
		logging.info(f"Number of tasks collected: {len(B)}");return B