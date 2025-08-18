import os,base64
from mimetypes import MimeTypes
CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR=os.path.join(CURRENT_DIR,'assets')
def get_image_base64(path):
	with open(path,'rb')as A:return base64.b64encode(A.read()).decode('utf-8')
def get_image_base64_local(path):return get_image_base64(os.path.join(ASSETS_DIR,path))
def get_logo_image_src(logo_file):
	A=logo_file
	if not A:A=os.path.join(ASSETS_DIR,'logo.svg')
	B=MimeTypes().guess_type(A)[0]or'image/*';C=get_image_base64(A);return f"data:{B};base64,"+C