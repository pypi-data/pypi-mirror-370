_E='charts'
_D='x_index'
_C='csv_col_index'
_B='curves'
_A=None
import logging
from dataclasses import dataclass,field
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
from scilens.config.models.reader_format_cols import ReaderCurveParserNameConfig
from scilens.config.models.reader_metrics import ReaderColsMetricsConfig
import math
def get_col_indexes(source,numeric_col_indexes,names):
	C=names;A=source;B=[]
	if not isinstance(A,list):A=[A]
	if isinstance(A[0],int):
		for F in A:B.append(F-1)
	else:
		for D in A:
			if D in C:B.append(C.index(D))
	for E in B:
		if E not in numeric_col_indexes:raise ValueError(f"Index column index {E} is not a numeric column.")
	return B
@dataclass
class ColsDataset:
	cols_count:int=0;rows_count:int=0;names:list[str]=field(default_factory=lambda:[]);numeric_col_indexes:list[int]=field(default_factory=lambda:[]);data:list[list[float]]=field(default_factory=lambda:[]);origin_line_nb:list[int]=field(default_factory=lambda:[])
	def get_col_indexes(A,col_x):return get_col_indexes(col_x,A.numeric_col_indexes,A.names)
	def get_curves_col_x(F,col_x):
		J='title';C=col_x;A=F;G={};H=F.get_col_indexes(C)
		if not H:raise ValueError(f"get_curves_col_x Column {C} not found in numeric columns.")
		D=H[0];G[_D]=D;K=[B for(A,B)in enumerate(A.numeric_col_indexes)if A!=D];E=[];I=[]
		for B in K:C=A.data[D];L=A.data[B];M={J:A.names[B],'short_title':A.names[B],'series':[[C[A],L[A]]for A in range(A.rows_count)],_C:B};E+=[M];N={J:A.names[B],'type':'simple','xaxis':A.names[D],'yaxis':A.names[B],_B:[len(E)-1]};I+=[N]
		return{_B:E,_E:I},G
	def compute_metrics(K,config):
		C=K;L={}
		for(H,F)in enumerate(config):
			I=F.name;B=F.col;J=F.function;D=F.aggregation
			if not B and not J:raise ValueError(f"Metric #{H} must have either a column or a function.")
			if B and J:raise ValueError(f"Metric #{H} cannot have both a column and a function.")
			if B:
				E=_A
				if isinstance(B,int):E=C.numeric_col_indexes.index(B-1)
				if isinstance(B,str):E=C.names.index(B)
				if E is _A or E<0 or E>=C.cols_count:raise ValueError(f"Metric #{H} has an invalid column: {B}.")
				if not I:I=f"{C.names[E]} {D}"
				A=C.data[E]
			elif J:
				A=[0 for A in range(C.rows_count)]
				if J=='euclidean_norm':
					if not I:I=f"Euclidean Norm {F.components} {D}"
					M=K.get_col_indexes(F.components)
					if not M:continue
					for N in M:
						for(O,P)in enumerate(C.data[N]):A[O]+=P**2
					A=[math.sqrt(A)for A in A]
				else:raise ValueError(f"Metric #{H} has an invalid function: {J}.")
			G=_A
			if D=='mean':G=sum(A)/len(A)
			elif D=='sum':G=sum(A)
			elif D=='min':G=min(A)
			elif D=='max':G=max(A)
			if G is _A:raise ValueError(f"Metric #{H} has an invalid aggregation: {D}.")
			L[I]=G
		return L
@dataclass
class ColsCurves:type:str;info:dict;curves:dict
def compare(group,compare_floats,reader_test,reader_ref,cols_curve):
	O='Errors limit reached';F=reader_ref;D=group;C=cols_curve;A=reader_test;logging.debug(f"compare cols: {D.name}")
	if len(A.numeric_col_indexes)!=len(F.numeric_col_indexes):D.error=f"Number Float columns indexes are different: {len(A.numeric_col_indexes)} != {len(F.numeric_col_indexes)}";return
	E=[''for A in range(A.cols_count)];I=_A;G=_A
	if C and C.type==ReaderCurveParserNameConfig.COL_X:J=C.info[_D];I=A.data[J];G=A.names[J]
	K=False
	for B in range(A.cols_count):
		if B not in A.numeric_col_indexes:continue
		P=A.data[B];Q=F.data[B];logging.debug(f"compare cols: {A.names[B]}");L,R,T=compare_floats.add_group_and_compare_vectors(A.names[B],D,{'info_prefix':G}if G else _A,P,Q,info_vector=I)
		if R:K=True;E[B]=O;continue
		if L.total_errors>0:E[B]=f"{L.total_errors} comparison errors"
	if C:
		for M in C.curves[_E]:
			N=0
			for S in M[_B]:
				H=C.curves[_B][S]
				if E[H[_C]]:H['comparison_error']=E[H[_C]];N+=1
			M['comparison']={'curves_nb_with_error':N}
	D.error=O if K else _A;D.info={'cols_has_error':E}