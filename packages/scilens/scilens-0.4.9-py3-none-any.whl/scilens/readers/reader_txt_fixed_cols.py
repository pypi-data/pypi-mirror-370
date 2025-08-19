_A=None
import logging,re
from itertools import islice
from dataclasses import dataclass
from scilens.readers.transform import string_2_float
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.cols_dataset import ColsDataset,ColsCurves,compare
from scilens.config.models import ReaderTxtFixedColsConfig
from scilens.config.models.reader_format_cols import ReaderCurveParserNameConfig
from scilens.components.compare_floats import CompareFloats
@dataclass
class ParsedHeaders:raw:str;cleaned:str;data:list[str];ori_line_idx:int|_A=_A
class ReaderTxtFixedCols(ReaderInterface):
	configuration_type_code='txt_fixed_cols';category='datalines';extensions=[]
	def _ignore_line(A,line):
		if not line.strip():return True
		if A.ignore_lines_patterns:
			for B in A.ignore_lines_patterns:
				if bool(re.match(B,line)):return True
		return False
	def _get_parsed_headers(A,path):
		B=A.reader_options;C=_A
		with open(A.origin.path,'r',encoding=A.encoding)as G:
			D=-1
			if B.has_header_line is not _A:
				for E in G:
					D+=1
					if D+1==B.has_header_line:C=E;break
			else:
				for E in G:
					D+=1
					if not A._ignore_line(E):C=E;break
		if C:
			H=C.strip();F=H
			if B.has_header_ignore:
				for I in B.has_header_ignore:F=F.replace(I,'')
			return ParsedHeaders(raw=H,cleaned=F,data=F.split(),ori_line_idx=D)
	def _get_first_data_line(A,path):
		D=A.reader_options;B=D.has_header
		with open(A.origin.path,'r',encoding=A.encoding)as E:
			for C in E:
				if not A._ignore_line(C):
					if B:B=False;continue
					else:return C
	def _discover_col_idx_ralgin_spaces(G,line):
		A=line;A=A.rstrip();C=[];D=_A;B=0
		for(E,F)in enumerate(A):
			if D is not _A and D!=' 'and F==' ':C.append((B,E));B=E
			D=F
		if B<len(A):C.append((B,len(A)))
		return C
	def _derive_col_indexes(A,header_row=_A):0
	def read(A,reader_options):
		B=reader_options;A.reader_options=B;A.ignore_lines_patterns=_A;I=_A;K=_A;D=B.cols
		if D:
			if D.rows:A.ignore_lines_patterns=D.rows.ignore_patterns;I=D.rows.line_start;K=D.rows.line_end
		F=A._get_parsed_headers(A.origin.path)if B.has_header else _A;L=open(A.origin.path,'r',encoding=A.encoding);E=[]
		if B.column_indexes or B.column_widths:
			if B.column_indexes and B.column_widths:raise Exception('column_indexes and column_widths are exclusive.')
			if B.column_widths:
				logging.debug(f"Using column widths: {B.column_widths}");J=0
				for M in B.column_widths:E+=[(J,J+M)];J+=M
			else:logging.debug(f"Using column indexes: {B.column_indexes}");E=B.column_indexes
		else:logging.debug(f"Using auto derived column indexes.");P=A._get_first_data_line(A.origin.path);E=A._discover_col_idx_ralgin_spaces(P)
		logging.debug(f"Column indexes: {E}")
		if not E:raise Exception('No column indexes or widths provided, and no headers found to derive column indexes.')
		G=len(E);C=ColsDataset(cols_count=G,names=[f"Column {A+1}"for A in range(G)],numeric_col_indexes=[A for A in range(G)],data=[[]for A in range(G)])
		if F:C.names=F.data
		if D and D.ignore_columns:
			if isinstance(D.ignore_columns[0],str):C.numeric_col_indexes=[A for A in C.numeric_col_indexes if C.names[A]not in D.ignore_columns]
			if isinstance(D.ignore_columns[0],int):Q=[A-1 for A in D.ignore_columns];C.numeric_col_indexes=[A for A in C.numeric_col_indexes if A not in Q]
		H=I or 0
		for N in islice(L,I,K):
			H+=1
			if A._ignore_line(N):continue
			if F:
				if F.ori_line_idx==H-1:continue
			for(R,O)in enumerate(E):S=N[O[0]:O[1]].strip();T=string_2_float(S);C.data[R].append(T)
			C.origin_line_nb.append(H)
		C.rows_count=len(C.origin_line_nb);L.close();A.cols_dataset=C;A.raw_lines_number=H;A.metrics=_A
		if B.metrics:A.metrics=C.compute_metrics(B.metrics)
		A.curves=_A;A.cols_curve=_A
		if B.cols and B.cols.curve_parser:
			if B.cols.curve_parser.name==ReaderCurveParserNameConfig.COL_X:
				A.curves,U=C.get_curves_col_x(B.cols.curve_parser.parameters.x)
				if A.curves:A.cols_curve=ColsCurves(type=ReaderCurveParserNameConfig.COL_X,info=U,curves=A.curves)
			elif B.cols.curve_parser.name==ReaderCurveParserNameConfig.COLS_COUPLE:raise NotImplementedError('cols_couple not implemented')
			else:raise Exception('Curve parser not supported.')
	def compare(A,compare_floats,param_reader,param_is_ref=True):D=param_is_ref;C=param_reader;B=compare_floats;E=A.cols_dataset if D else C.cols_dataset;F=A.cols_dataset if not D else C.cols_dataset;G=A.cols_curve;I,H=B.compare_errors.add_group('node','txt cols');return compare(H,B,E,F,G)
	def class_info(A):return{'cols':A.cols_dataset.names,'raw_lines_number':A.raw_lines_number,'curves':A.curves,'metrics':A.metrics}