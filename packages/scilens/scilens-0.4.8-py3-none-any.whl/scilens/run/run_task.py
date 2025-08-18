import logging,os
from enum import Enum
from pydantic import BaseModel
from scilens.config.models import AppConfig
from scilens.run.models.task_results import TaskResults
from scilens.run.models.task_runtime import TaskRuntime
from scilens.run.task_context import TaskContext
from scilens.processors.models.results import ProcessorResults
from scilens.processors import Analyse,Compare,ExecuteAndCompare
from scilens.report.report import Report
from scilens.utils.system import info as system_info
from scilens.utils.time_tracker import TimeTracker
from scilens.utils.template import template_render_string
from scilens.config.models.base import is_StrOrPath_and_path
def var_render(value,runtime):return template_render_string(value,runtime.model_dump())
def runtime_process_vars(config):
	A=TaskRuntime(sys=system_info(),env=os.environ.copy(),vars={})
	for(B,C)in config.variables.items():A.vars[B]=var_render(C,A)
	return A
def runtime_apply_to_config(runtime,config_model,working_dir):
	G=working_dir;D=runtime;B=config_model
	for(C,H)in B.__class__.__pydantic_fields__.items():
		A=getattr(B,C);I,E=is_StrOrPath_and_path(A,H)
		if I:
			F=os.path.join(G,E)if not os.path.isabs(E)else E
			if not os.path.exists(F):raise Exception(f"Config {C}: {A} Path '{F}' does not exist.")
			else:
				with open(F,'r')as J:A=J.read();setattr(B,C,A)
		K=issubclass(A.__class__,BaseModel);L=isinstance(A.__class__,type)and issubclass(A.__class__,Enum);M=isinstance(A,str);N=isinstance(A,list)and all(isinstance(A,str)for A in A);O=isinstance(A,dict)and all(isinstance(A,str)and isinstance(B,str)for(A,B)in A.items())
		if K:runtime_apply_to_config(D,A,G)
		elif M and not L:setattr(B,C,var_render(A,D))
		elif N:setattr(B,C,[var_render(A,D)for A in A])
		elif O:setattr(B,C,{A:var_render(B,D)for(A,B)in A.items()})
class RunTask:
	def __init__(A,context):A.context=context
	def _get_processors(A):return{A.__name__:A for A in[Analyse,Compare,ExecuteAndCompare]}
	def process(A):
		logging.info(f"Running task");logging.info(f"Prepare runtime variables");H=runtime_process_vars(A.context.config);logging.info(f"Apply runtime variables to config");runtime_apply_to_config(H,A.context.config,A.context.working_dir);logging.debug(f"on working_dir '{A.context.working_dir}'");logging.debug(f"with origin_working_dir '{A.context.origin_working_dir}'");logging.debug(f"with config {A.context.config.model_dump_json(indent=4)}");C=A.context.config.processor
		if not C:raise Exception('Processor not defined in config.')
		D=A._get_processors().get(C)
		if not D:raise Exception('Processor not found.')
		logging.info(f"Processor '{D.__name__}'")
		try:F=TimeTracker();G=D(A.context);E=G.process();F.stop();I=F.get_data()
		except Exception as B:logging.error(B);return TaskResults(error=str(B))
		finally:G=None
		try:J=Report(A.context.working_dir,[A.context.origin_working_dir],A.context.config.report,A.context.task_name).process({'meta':{'system_info':system_info(),'task_info':{'processor':C,'process_time':I}},'processor_results':E.data},C)
		except Exception as B:logging.error(B);return TaskResults(error=str(B),processor_results=E)
		return TaskResults(processor_results=E,report_results=J)