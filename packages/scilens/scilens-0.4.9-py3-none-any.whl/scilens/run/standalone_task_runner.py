import logging
from scilens.config.load import config_load
from scilens.run.task_context import TaskContext
from scilens.run.run_task import RunTask
from scilens.config.models import AppConfig
class StandaloneTaskRunner:
	config:AppConfig;config_path=None
	def __init__(A,config,config_override=None):A.config=config_load(config,config_override=config_override)
	def process(A,working_dir,origin_working_dir=None):B=TaskContext(config=A.config,config_file=A.config_path,working_dir=working_dir,origin_working_dir=origin_working_dir);C=RunTask(B);D=C.process();return D