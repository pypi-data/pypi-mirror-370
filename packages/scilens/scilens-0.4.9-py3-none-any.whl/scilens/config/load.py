import logging,os,json,yaml
from pydantic import BaseModel
from scilens.config.models import AppConfig
from scilens.config.env_var import get_vars
from scilens.utils.dict import dict_path_set,dict_path_get,dict_update_rec
PATH_ENV_VARS_VALUES={}
def env_vars_load():
	B=get_vars()
	for(C,D)in B.items():
		A=os.getenv(C)
		if A:PATH_ENV_VARS_VALUES[D]=A
env_vars_load()
def config_load(config,options_path_value=None,config_override=None):
	F=options_path_value;B=config_override;A=config;J=isinstance(A,str)or isinstance(B,str);K=bool(PATH_ENV_VARS_VALUES);L=bool(F)
	if isinstance(A,str):
		logging.info(f"Loading configuration file {A}")
		with open(A,'r')as G:
			try:C=yaml.safe_load(G)
			except yaml.YAMLError as D:raise Exception(f"Error in configuration file {A}: {D}")
	elif isinstance(A,dict):C=json.loads(json.dumps(A))
	if B:
		if isinstance(B,str):
			logging.info(f"Loading configuration file {B}")
			with open(B,'r')as G:
				try:I=yaml.safe_load(G)
				except yaml.YAMLError as D:raise Exception(f"Error in configuration file {B}: {D}")
		elif isinstance(A,dict):I=B
		dict_update_rec(C,I)
	for(E,H)in PATH_ENV_VARS_VALUES.items():
		if not dict_path_get(C,E):dict_path_set(C,E,H)
	if F:
		for(E,H)in F.items():dict_path_set(C,E,H)
	try:return AppConfig(**C)
	except Exception as D:
		logging.error(f"Error in configuration definition")
		if J:logging.error(f"Please check Configuration file: {A}")
		if K:logging.error(f"Please check Environment Variables")
		if L:logging.error(f"Please check Command Options")
		logging.warning(f"{D}");exit(1)
def pydantic_to_yaml(model):return yaml.safe_dump(model.model_dump(by_alias=True),default_flow_style=False)