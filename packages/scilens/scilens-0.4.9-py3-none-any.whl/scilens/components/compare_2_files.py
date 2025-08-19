import os,re
from scilens.run.task_context import TaskContext
from scilens.readers.reader_interface import ReaderInterface
from scilens.components.file_reader import FileReader
from scilens.components.compare_models import SEVERITY_ERROR,SEVERITY_WARNING
from scilens.components.compare_errors import CompareErrors
from scilens.components.compare_floats import CompareFloats
class Compare2Files:
	def __init__(A,context):A.context=context
	def compare(B,path_test,path_ref):
		i='status';h='severity';g='comparison_errors';f='comparison';Y=path_ref;X=path_test;W='err_index';V='reader';U='skipped';T=None;R='metrics';Q='error';P=True;O='ref';K='path';J='test';A={J:{},O:{},f:T,g:T};H={J:{K:X},O:{K:Y}};S=B.context.config.compare.sources.not_matching_source_ignore_pattern
		for(C,L)in H.items():
			if not L.get(K)or not os.path.exists(L[K]):
				if S:
					if S=='*':A[U]=P;return A
					else:
						j=os.path.basename(Y if C==J else X);k=re.search(S,j)
						if k:A[U]=P;return A
				A[Q]=f"file {C} does not exist";return A
		l=FileReader(B.context.working_dir,B.context.config.file_reader,B.context.config.readers,config_alternate_path=B.context.origin_working_dir)
		for(C,L)in H.items():H[C][V]=l.read(L[K])
		D=H[J][V];F=H[O][V]
		if not D or not F:A[U]=P;return A
		A[J]=D.info();A[O]=F.info()
		if D.read_error:A[Q]=D.read_error;return A
		E=CompareErrors(B.context.config.compare.errors_limit,B.context.config.compare.ignore_warnings);Z=CompareFloats(E,B.context.config.compare.float_thresholds);a=D.compare(Z,F,param_is_ref=P);G=E.root_group;M=T
		if B.context.config.compare.metrics_compare and(D.metrics or F.metrics):
			o,M=E.add_group(R,R,parent=G)
			if B.context.config.compare.metrics_thresholds:b=CompareFloats(E,B.context.config.compare.metrics_thresholds)
			else:b=Z
			b.compare_dicts(D.metrics,F.metrics,M)
		I={'total_diffs':G.total_diffs}
		if G.info:I.update(G.info)
		if a:I.update(a)
		if M:
			N={}
			for c in[SEVERITY_ERROR,SEVERITY_WARNING]:
				for(m,d)in enumerate(E.errors[c]):
					if d.group==M.id:N[d.info['key']]={h:c,W:m}
			I[R]={}
			for C in D.metrics.keys():I[R][C]={i:N[C][h],W:N[C][W]}if C in N else{i:'success'}
		A[f]=I;A[g]=E.get_data()
		if G.error:A[Q]=G.error;return A
		D.close();F.close();e=len(E.errors[SEVERITY_ERROR])
		if e>0:n=f"{e} comparison errors";A[Q]=n
		return A