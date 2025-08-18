from functools import reduce
def dict_path_set(obj,path,value):
	A=obj;B=path.split('.')
	for C in B[:-1]:A=A.setdefault(C,{})
	A[B[-1]]=value
def dict_path_get(obj,path):return reduce(dict.get,path.split('.'),obj)
def dict_update_rec(base,updates):
	A=base
	for(B,C)in updates.items():
		if B in A and isinstance(A[B],dict)and isinstance(C,dict):dict_update_rec(A[B],C)
		else:A[B]=C