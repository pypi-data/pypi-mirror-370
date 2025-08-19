from pathlib import Path
from scilens.utils.file import json_load,yaml_load
def load_model_from_file(cls,path,json=True,yaml=True):
	C=yaml;B=json;A=path
	if isinstance(A,str):A=Path(A)
	if not A.exists():raise FileNotFoundError(f"File {A} does not exist.")
	if B:
		try:D=json_load(A)
		except Exception:
			if not C:raise ValueError(f"Error during loading JSON file: {A}.")
	if C:
		try:D=yaml_load(A)
		except Exception:
			if not B:raise ValueError(f"Error during loading YAML file: {A}.")
	if B and C and not D:raise ValueError(f"Unsupported file format: Supported formats are YAML and JSON.")
	E=cls(**D);return E