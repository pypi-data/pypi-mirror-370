import requests
from urllib.parse import urlparse
BASE_HEADERS={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
class Web:
	def download(E,url,filename,headers=None):
		A=headers;B=BASE_HEADERS.copy()
		if A:B.update(A)
		C=requests.get(url,headers=B);C.raise_for_status()
		with open(filename,'wb')as D:D.write(C.content)
	def download_progress(L,url,filename,headers=None,callback100=None):
		E=callback100;D=headers;F=BASE_HEADERS.copy()
		if D:F.update(D)
		A=requests.get(url,headers=F,stream=True)
		if A.status_code>299:raise ValueError(f"Error downloading file: {A.status_code} - {A.text}")
		I=int(A.headers.get('Content-Length',0));G=0;J=I//100;B=0
		with open(filename,'wb')as K:
			for C in A.iter_content(chunk_size=1024):
				if C:
					K.write(C);G+=len(C);H=G//J
					if H>B:
						B=H
						if E:E(B)