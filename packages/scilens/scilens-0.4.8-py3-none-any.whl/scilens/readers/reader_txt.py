_F='floats'
_E='lines'
_D=True
_C=False
_B='line'
_A=None
import re
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.transform import string_2_floats
from scilens.config.models import ReaderTxtConfig
from scilens.components.compare_models import SEVERITY_ERROR,Compare2ValuesResults
from scilens.components.compare_floats import CompareFloats
class ReaderTxt(ReaderInterface):
	configuration_type_code='txt';category='datalines';extensions=['TXT']
	def read(A,config):
		I='_';B=config;A.reader_options=B;A.get_lines_pre=1;A.get_lines_post=1
		if B.report_lines:
			C=_C
			for(M,J)in B.report_lines.items():
				if M==A.origin.short_name:C=_D;A.get_lines_pre=J.pre;A.get_lines_post=J.post
			if not C and B.report_lines.get(I):A.get_lines_pre=B.report_lines[I].pre;A.get_lines_post=B.report_lines[I].post
		D=_A
		if B.ignore:
			C=_C
			for(M,J)in B.ignore.items():
				if M==A.origin.short_name:C=_D;D=J
			if not C and B.ignore.get(I):D=B.ignore[I]
		P=open(A.origin.path,'r',encoding=A.encoding);A.raw_lines=P.readlines();P.close();A.raw_lines_number=len(A.raw_lines);E=[]
		if D:
			C,R=A.find_patterns_lines_nb([A.pattern for A in D])
			for(S,Q)in enumerate(D):
				K=R[S][_E]
				if K:K=A.get_raw_siblings_nb(K,pre=Q.pre,post=Q.post);E+=K
			E=list(set(E));E.sort()
		A.ignore_patterns=[A.pattern for A in D]if D else[];A.ignore_lines=E;A.ignore_lines_number=len(E);A.curves=A.curve_parser(A.raw_lines)if A.curve_parser else _A;N=[]
		for(T,L)in enumerate(A.raw_lines):
			G=string_2_floats(L)
			if G:
				H=T+1
				if not H in E:N.append({_B:H,_F:G})
		A.floats_lines=N;A.floats_lines_number=len(N)
		if B.error_rule_patterns:
			C,U=A.find_patterns_lines_nb(B.error_rule_patterns);A.read_data['error_rule_patterns']={'found':C,'data':U}
			if C:A.read_error='String error pattern found'
		A.metrics=_A
		if B.metrics:
			O={}
			for F in B.metrics:
				L,H=A.find_pattern_first_line(F.pattern)
				if L:
					G=string_2_floats(L)
					if not G:raise ValueError(f"Metric pattern '{F.pattern}' found but no float values in the line number: {H}")
					try:V=G[F.number_position-1]
					except IndexError:raise ValueError(f"Metric pattern '{F.pattern}' found but no float value at position {F.number_position} in the line number: {H}")
					O[F.name or F.pattern]=V
			if O:A.metrics=O
	def compare(I,compare_floats,param_reader,param_is_ref=_D):
		U='diff';K=param_is_ref;J=param_reader;A=compare_floats;V,L=A.compare_errors.add_group('node','txt');V,B=A.compare_errors.add_group(_E,_E,parent=L);C=I if K else J;D=I if not K else J;E=_C
		if C.floats_lines_number!=D.floats_lines_number:L.error=f"Nb number lines 1: {C.floats_lines_number} 2: {D.floats_lines_number} different"
		M=C.floats_lines;W=D.floats_lines
		for N in range(len(M)):
			F=M[N];G=W[N];H=F[_F];O=G[_F];P={'line_nb_1':F[_B],'line_nb_2':G[_B],'line_1':C.get_raw_lines(F[_B]),'line_2':D.get_raw_lines(G[_B])}
			if len(H)!=len(O):
				if not E:B.incr(U);E=A.compare_errors.add(B,Compare2ValuesResults(SEVERITY_ERROR,'Not same numbers number in the lines'),info=P)
				continue
			for Q in range(len(H)):
				R=H[Q];S=O[Q];X=R-S
				if X==0:continue
				else:
					B.incr(U)
					if not E:
						T=A.compare_2_values(R,S)
						if T:E=A.compare_errors.add(B,T,info=P)
	def find_patterns_lines_nb(D,patterns):
		A=patterns;B=_C;map={A:[]for A in A}
		for(E,F)in enumerate(D.raw_lines):
			for C in A:
				if F.find(C)!=-1:map[C].append(E+1);B=_D
		return B,[{'pattern':A,_E:map[A]}for A in A]
	def find_pattern_first_line(B,pattern):
		for(C,A)in enumerate(B.raw_lines):
			D=re.search(pattern,A)
			if D:return A.strip(),C+1
	def get_raw_siblings_nb(A,lines_nb_array,pre=_A,post=_A):
		B=[]
		for C in lines_nb_array:
			min=C-(pre if pre is not _A else A.get_lines_pre);max=C+(post if post is not _A else A.get_lines_post)+1
			if min<0:min=0
			if max>A.raw_lines_number+1:max=A.raw_lines_number+1
			for D in range(min,max):
				if D not in B:B.append(D)
		return B
	def get_raw_lines(A,line_nb,pre=_A,post=_A):
		B=line_nb;min=B-1-(pre if pre is not _A else A.get_lines_pre);max=B-1+(post if post is not _A else A.get_lines_post)+1
		if min<0:min=0
		if max>A.raw_lines_number:max=A.raw_lines_number
		return''.join([A.raw_lines[B]for B in range(min,max)])
	def class_info(A):return{'raw_lines_number':A.raw_lines_number,'ignore_patterns':A.ignore_patterns,'ignore_lines_number':A.ignore_lines_number,'ignore_lines':A.ignore_lines,'floats_lines_number':A.floats_lines_number,'curves':A.curves,'metrics':A.metrics}