_A=None
import csv
from collections.abc import Iterator
from dataclasses import dataclass,field,asdict
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
@dataclass
class MatDataset:x_name:str;y_name:str;nb_lines:int=0;nb_columns:int=0;data:list[list[float]]=field(default_factory=lambda:[]);x_values:list[float]|_A=_A;y_values:list[float]|_A=_A
def from_iterator(x_name,y_name,reader,x_value_line=_A,has_header=False,has_y=False):
	E=has_y;D=x_value_line;B=reader;H=_A;I=[]if E else _A;A=[];F=0
	if D:
		J=1 if E else 0
		for M in range(0,D):
			K=next(B);F+=1
			if F==D:H=[float(A)for A in K[J:]]
	if F==0 and has_header:next(B)
	if E:
		for C in B:L=float(C[0]);G=[float(A)for A in C[1:]];I.append(L);A.append(G)
	else:
		for C in B:G=[float(A)for A in C];A.append(G)
	return MatDataset(x_name=x_name,y_name=y_name,nb_lines=len(A),nb_columns=len(A[0])if len(A)>0 else 0,data=A,x_values=H,y_values=I)
def compare(parent_group,compare_floats,test,ref,group_name=''):B=parent_group;A=test;D,C,E=compare_floats.add_group_and_compare_matrices(group_name,B,group_data=_A,test_mat=A.data,ref_mat=ref.data,x_vector=A.x_values,y_vector=A.y_values);B.error='Errors limit reached'if C else _A
def get_data(datasets,names,frameseries_steps_data=_A,frameseries_steps_name=_A):
	B=names;A=datasets
	if len(A)!=len(B):raise ValueError('Datasets and names must have the same length')
	C={'datasets':[asdict(A)for A in A],'names':B};return C