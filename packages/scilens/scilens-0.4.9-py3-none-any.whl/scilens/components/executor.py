_A=None
import logging,os,shutil,stat,subprocess,platform,tempfile,zipfile
from scilens.config.models import ExecuteConfig
from scilens.utils.file import dir_remove,dir_create
from scilens.utils.web import Web
def unzip_file(zip_file_path,extract_to_path):
	with zipfile.ZipFile(zip_file_path,'r')as A:A.extractall(extract_to_path)
def find_command(command_path,working_dirs,guess_os_extension=False):
	J='.bash';I='.sh';G=working_dirs;A=command_path;H=os.path.isabs(A);C=[]
	if guess_os_extension:
		D=platform.system().lower()
		if D=='windows':C=['.exe','.bat','.cmd']
		elif D=='linux':C=[I,J,'.bin']
		elif D=='darwin':C=[I,J]
		else:logging.warning(f"Unknown system {D}")
	if H:
		if os.path.exists(A):return A
	else:
		for E in G:
			B=os.path.join(E,A)
			if os.path.exists(B):return B
	for K in C:
		F=A+K
		if H:
			if os.path.exists(F):return F
		else:
			for E in G:
				B=os.path.join(E,F)
				if os.path.exists(B):return B
class Executor:
	def __init__(A,absolute_working_dir,config,config_file_path=_A,alternative_working_dir=_A):
		D=alternative_working_dir;C=absolute_working_dir;B=config;A.config=B;A.config_file_path=config_file_path;A.working_dir=C;A.dirs=[C]+([D]if D else[]);A.command_path=_A;A.temp_dir=_A
		if not bool(B.exe_url)+bool(B.exe_url)!=1:raise Exception('exe_url and exe_path are mutually exclusive.')
		if not os.path.exists(A.working_dir):logging.info(f"Creating working directory {A.working_dir}");dir_create(A.working_dir)
	def __enter__(A):return A
	def __exit__(A,exc_type,exc_value,traceback):A._cleanup()
	def _cleanup(A):0
	def _pre_operations(A):
		D=A.working_dir;logging.info(f"Execute - Pre Operations")
		if A.config.pre_files_delete:
			logging.info(f"Files deletion")
			for F in os.listdir(D):
				E=os.path.join(D,F)
				if not F.startswith('.')and not os.path.isdir(E)and E!=A.config_file_path:logging.debug(f"Delete file {E}");os.remove(E)
		logging.info(f"Folders deletion")
		for dir in A.config.pre_folder_delete or[]:dir_remove(os.path.join(D,dir))
		logging.info(f"Folders creation")
		for dir in A.config.pre_folder_creation or[]:dir_create(os.path.join(D,dir))
		if A.config.exe_url or A.config.exe_path:
			logging.info(f"Executable file preparation")
			if A.config.exe_url:
				logging.info(f"Download executable {A.config.exe_url}");A.temp_dir=tempfile.mkdtemp();H='executable';B=os.path.join(A.temp_dir,H)
				try:Web().download_progress(A.config.exe_url,B,headers=A.config.exe_url_headers,callback100=lambda percentage:logging.info(f"Downloaded {percentage}%"))
				except Exception as I:raise ValueError(f"Error downloading executable: {I}")
				logging.info(f"Download completed")
			elif A.config.exe_path:B=A.config.exe_path
			if A.config.exe_unzip_and_use:logging.info(f"Unzip archive");G=os.path.dirname(B);unzip_file(B,G);B=os.path.join(G,A.config.exe_unzip_and_use);logging.info(f"Unzip completed")
			C=find_command(B,A.dirs,guess_os_extension=A.config.exe_guess_os_extension)
			if not C:raise FileNotFoundError(f"Command not found: {B}")
			logging.info(f"Command path resolved: {C}");logging.info(f"Add executable permissions");J=os.stat(C).st_mode;os.chmod(C,J|stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH)
		elif A.config.exe_command:logging.info(f"Command path: {A.config.exe_command}");C=A.config.exe_command
		A.command_path=C
	def _post_operations(A):logging.info(f"Execute - Post Operations")
	def _run_command(A):logging.info(f"Execute - Run Command");C=A.command_path;B=f"{C}{A.config.command_suffix or''}";logging.info(f"RUN COMMAND {B} in {A.working_dir}");subprocess.run(B,shell=True,check=True,cwd=A.working_dir)
	def process(A):logging.info(f"Execute");A._pre_operations();A._run_command();A._post_operations();A._cleanup()