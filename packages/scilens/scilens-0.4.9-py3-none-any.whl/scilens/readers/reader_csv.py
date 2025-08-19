_B=True
_A=None
import logging,csv,re
from scilens.readers.reader_interface import ReaderInterface
from scilens.readers.cols_dataset import ColsDataset,ColsCurves,compare as cols_compare,get_col_indexes
from scilens.readers.mat_dataset import MatDataset,from_iterator as mat_from_iterator,compare as mat_compare,get_data
from scilens.config.models.reader_format_csv import ReaderCsvConfig,ReaderCsvMatrixConfig
from scilens.config.models.reader_format_cols import ReaderCurveParserNameConfig
from scilens.components.compare_models import CompareGroup
from scilens.components.compare_floats import CompareFloats
def is_num(x):
	try:return float(x)
	except ValueError:return
def csv_row_detect_header(first_row):
	A=first_row
	if all(not A.isdigit()for A in A):return _B,A
	else:return False,[f"Column {A}"for(A,B)in enumerate(A)]
def csv_row_detect_cols_num(row):return[A for(A,B)in enumerate(row)if is_num(B)!=_A]
def csv_detect(path,delimiter,quotechar,encoding):
	with open(path,'r',encoding=encoding)as B:A=csv.reader(B,delimiter=delimiter,quotechar=quotechar);C=next(A);D,E=csv_row_detect_header(C);F=next(A);G=csv_row_detect_cols_num(F);return D,E,G
class ReaderCsv(ReaderInterface):
	configuration_type_code='csv';category='datalines';extensions=['CSV']
	def _ignore_line(A,line):
		if not line.strip():return _B
		if A.ignore_lines_patterns:
			for B in A.ignore_lines_patterns:
				if bool(re.match(B,line)):return _B
		return False
	def read(A,reader_options):
		C=reader_options;A.reader_options=C;F,L,V=csv_detect(A.origin.path,A.reader_options.delimiter,A.reader_options.quotechar,encoding=A.encoding);A.has_header=F;A.cols=L;A.numeric_col_indexes=V;A.index_col_index=_A;A.ignore_lines_patterns=_A;G=_A;H=_A;I=_A;J=_A;B=C.cols
		if B:
			if B.index_col:
				if B.index_col:R=get_col_indexes(B.index_col,A.numeric_col_indexes,L);A.index_col_index=R[0]if R else _A
			if B.rows:
				A.ignore_lines_patterns=B.rows.ignore_patterns;G=B.rows.line_start;H=B.rows.line_end
				if G and H and H<G:raise ValueError(f"Line end {H} cannot be before line start {G}.")
				if B.rows.index_min_value or B.rows.index_max_value:
					if A.index_col_index is _A:raise ValueError('Index column must be defined to use index min/max values.')
					I=B.rows.index_min_value;J=B.rows.index_max_value
					if I and J and I>J:raise ValueError(f"Index min value {I} cannot be greater than index max value {J}.")
		A.raw_lines_number=_A;A.curves=_A;A.report_matrices=_A
		with open(A.origin.path,'r',encoding=A.encoding)as W:
			S=W.readlines();M=csv.reader(S,delimiter=A.reader_options.delimiter,quotechar=A.reader_options.quotechar)
			if C.is_matrix:
				K=C.matrix or ReaderCsvMatrixConfig();P=mat_from_iterator(x_name=K.x_name,y_name=K.y_name,reader=M,has_header=F,x_value_line=K.x_value_line,has_y=K.has_y)
				if K.export_report:A.report_matrices=get_data([P],['csv'])
				A.mat_dataset=P;A.raw_lines_number=P.nb_lines+(1 if F else 0)
			else:
				if C.cols and C.cols.ignore_columns:
					if not F:raise Exception('Ignore columns is not supported without header.')
					if isinstance(C.cols.ignore_columns[0],str):A.numeric_col_indexes=[B for B in A.numeric_col_indexes if A.cols[B]not in C.cols.ignore_columns]
					if isinstance(C.cols.ignore_columns[0],int):X=[A-1 for A in B.ignore_columns];A.numeric_col_indexes=[A for A in A.numeric_col_indexes if A not in X]
				T=len(L);D=ColsDataset(cols_count=T,names=L,numeric_col_indexes=A.numeric_col_indexes,data=[[]for A in range(T)]);E=0
				if F and E==0:next(M);E+=1
				if G:
					try:
						while _B:
							if G<=E+1:break
							N=next(M);E+=1
					except StopIteration:pass
				try:
					while _B:
						N=next(M);E+=1
						if H and E>H:break
						if J is not _A and float(N[A.index_col_index])>J:break
						if A.ignore_lines_patterns and A._ignore_line(S[E-1].rstrip('\n')):continue
						if I is not _A and float(N[A.index_col_index])<I:continue
						for(U,Q)in enumerate(N):
							if U in D.numeric_col_indexes:Q=float(Q)
							D.data[U].append(Q)
						D.origin_line_nb.append(E)
				except StopIteration:pass
				D.rows_count=len(D.origin_line_nb);A.cols_dataset=D;A.raw_lines_number=D.rows_count+(1 if F else 0);A.metrics=_A
				if C.metrics:A.metrics=D.compute_metrics(C.metrics)
				if B and B.curve_parser:
					if B.curve_parser.name==ReaderCurveParserNameConfig.COL_X:
						O=_A
						if B.curve_parser.parameters:O=B.curve_parser.parameters.x
						elif B.index_col:O=B.index_col
						if not O:raise ValueError('Curve parser COL_X requires a parameter x, or index_col to be defined.')
						A.curves,Y=D.get_curves_col_x(O)
						if A.curves:A.cols_curve=ColsCurves(type=ReaderCurveParserNameConfig.COL_X,info=Y,curves=A.curves)
					elif B.curve_parser.name==ReaderCurveParserNameConfig.COLS_COUPLE:raise NotImplementedError('cols_couple not implemented')
					else:raise Exception('Curve parser not supported.')
	def compare(A,compare_floats,param_reader,param_is_ref=_B):
		H='node';D=param_is_ref;C=param_reader;B=compare_floats;I=A.reader_options
		if I.is_matrix:E=A.mat_dataset if D else C.mat_dataset;F=A.mat_dataset if not D else C.mat_dataset;J,G=B.compare_errors.add_group(H,'csv matrix');mat_compare(G,B,E,F)
		else:E=A.cols_dataset if D else C.cols_dataset;F=A.cols_dataset if not D else C.cols_dataset;K=A.cols_curve if hasattr(A,'cols_curve')else _A;J,G=B.compare_errors.add_group(H,'csv cols');cols_compare(G,B,E,F,K)
	def class_info(A):return{'cols':A.cols,'raw_lines_number':A.raw_lines_number,'curves':A.curves,'matrices':A.report_matrices,'metrics':A.metrics}