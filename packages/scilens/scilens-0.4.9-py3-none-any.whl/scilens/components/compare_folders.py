_E='ref'
_D='name'
_C=None
_B='test'
_A='path'
import logging,os
from scilens.run.task_context import TaskContext
from scilens.components.compare_2_files import Compare2Files
def list_dir(path,filename_match_ignore,recursive,exclude_filepaths=_C):
	H=exclude_filepaths;G=filename_match_ignore;F='rel_path';E='filename_clean';A=path;A=os.path.normpath(A)
	if recursive:
		B=[]
		for(C,K,J)in os.walk(A):
			for I in J:B.append({_A:os.path.join(C,I),E:I.replace(str(G),''),F:C.replace(A+os.path.sep,'')if C!=A else''})
		D={os.path.join(A[F],A[E]):A for A in B}
	else:B={B.replace(str(G),''):B for B in os.listdir(A)if os.path.isfile(os.path.join(A,B))};D={B:{_A:os.path.join(A,C),E:B,F:''}for(B,C)in B.items()}
	return{B:A for(B,A)in D.items()if A[_A]not in H}if H else D
class CompareFolders:
	def __init__(A,context):B=context;A.context=B;C=B.config.compare.sources;A.cfg=C;A.test_base=os.path.join(B.working_dir,C.test_folder_relative_path);A.ref_base=os.path.join(B.working_dir,C.reference_folder_relative_path);A.test=A.test_base;A.ref=A.ref_base
	def compute_list_filenames(A):
		N='reference';I='filename_match_ignore';C='dict_files';logging.info(f"Comparing folders content: test vs reference");logging.debug(f"Comparing folders content: {A.test} vs {A.ref}")
		if A.test==A.ref:logging.warning(f"Test and reference folders are the same: {A.test}. No comparison will be done.");return[]
		O=[A.context.config_file]if A.context.config_file else _C;J=[];K=A.context.config.compare.sources.additional_path_suffixes or[''];E={_B:{C:{},_A:A.test,I:A.cfg.test_filename_match_ignore},N:{C:{},_A:A.ref,I:A.cfg.reference_filename_match_ignore}}
		for(L,D)in E.items():
			logging.info(f"Listing files in {L} folder");logging.debug(f"-- {L} folder: {D[_A]}")
			for M in K:
				F=list_dir(os.path.join(D[_A],M),D[I],A.cfg.recursive,exclude_filepaths=O)
				if len(K)>1:F={os.path.join(M,A):B for(A,B)in F.items()}
				D[C].update(F)
		G=E[_B][C];H=E[N][C];P=sorted(list(set(G.keys())|set(H.keys())))
		for B in P:J.append({_D:B,_B:G[B][_A]if G.get(B)else _C,_E:H[B][_A]if H.get(B)else _C})
		return J
	def compute_comparison(E,items):
		C='error';D=[]
		for B in items:
			logging.info(f"Comparing file: {B[_D]}")
			try:A=Compare2Files(E.context).compare(B[_B],B[_E])
			except Exception as F:A={C:str(F),_B:{},_E:{}}
			A[_D]=B[_D];D.append(A)
			if A.get(C):
				logging.warning(f"Error found in comparison: {A[C]}")
				if A[C]=='No reader found':logging.warning(f"Maybe Config Options could used to derive the correct reader or skip the file");logging.warning(f" - file_reader.extension_unknown_ignore to skip");logging.warning(f" - file_reader.extension_fallback to use a default reader");logging.warning(f" - file_reader.extension_mapping to map extensions")
		return D