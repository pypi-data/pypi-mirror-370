_A=None
import json,os,shutil,yaml
def file_remove(path):
	if os.path.exists(path):os.remove(path)
def dir_remove(path):
	if os.path.exists(path):shutil.rmtree(path)
def dir_create(path):
	if not os.path.exists(path):os.makedirs(path)
def dir_copy(source_dir,target_dir):shutil.copytree(source_dir,target_dir)
def dir_is_empty(path):return len(os.listdir(path))==0
def file_copy(source_file,destination_file):A=destination_file;os.makedirs(os.path.dirname(A),exist_ok=True);shutil.copy(source_file,A)
def copy(src,dst):
	A=src
	if os.path.isfile(A):file_copy(A,dst)
	else:dir_copy(A,dst)
def text_write(path,data,encoding=_A):
	with open(path,'w',encoding=encoding)as A:A.write(data)
def text_append(path,data,encoding=_A):
	with open(path,'a',encoding=encoding)as A:A.write(data)
def text_load(path,encoding=_A):
	with open(path,'r',encoding=encoding)as A:return A.read()
def json_write(path,data,encoding=_A):
	with open(path,'w',encoding=encoding)as A:json.dump(data,A,indent=4)
def json_write_small(path,data,encoding=_A):
	with open(path,'w',encoding=encoding)as A:json.dump(data,A)
def json_load(path,encoding=_A):
	with open(path,'r',encoding=encoding)as A:return json.load(A)
def yaml_write(path,data,encoding=_A):
	with open(path,'w',encoding=encoding)as A:yaml.dump(data,A,default_flow_style=False)
def yaml_load(path,encoding=_A):
	with open(path,'r',encoding=encoding)as A:return yaml.safe_load(A)
def move(source,target):shutil.move(source,target)
def list_paths_at_depth(root_dir,depth):
	B=depth;A=root_dir;C=[]
	for(D,F,G)in os.walk(A):
		E=D.count(os.sep)-A.count(os.sep)
		if E==B:C.append(D)
		elif E>B:F.clear()
	return C
def list_paths_for_file_recursive(path,filename):
	B=filename;A=path;C=[];D=os.path.join(A,B)
	if os.path.isfile(D):return[A]
	else:
		E=[os.path.join(A,B)for B in os.listdir(A)if os.path.isdir(os.path.join(A,B))]
		for dir in E:C+=list_paths_for_file_recursive(dir,B)
	return C