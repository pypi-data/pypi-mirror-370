_D='amplitude'
_C='diff'
_B=False
_A=None
import logging
from scilens.components.compare_models import SEVERITY_ERROR,SEVERITY_WARNING,CompareGroup,CompareFloatsErr,Compare2ValuesResults
from scilens.components.compare_errors import CompareErrors
from scilens.config.models import CompareFloatThresholdsConfig
try:from scilens_compare import vectors as CheckVectors
except ModuleNotFoundError:pass
def vector_get_amplitude(vector):min_val=min(vector);max_val=max(vector);return{'min':min_val,'max':max_val,_D:abs(max_val-min_val)}
class CompareFloats:
	def __init__(self,compare_errors,config):self.compare_errors=compare_errors;self.thresholds=config
	def compare_2_values(self,test,reference):
		thr=self.thresholds;sign=-1 if test-reference<0 else 1
		if abs(test)>thr.relative_vs_absolute_min and reference!=0:
			err=abs(test-reference)/abs(reference);comp_err=CompareFloatsErr(is_relative=True,value=sign*err,test=test,reference=reference)
			if err<thr.relative_error_max:
				if err>thr.relative_error_min:return Compare2ValuesResults(SEVERITY_WARNING,f"Rel. err. > {thr.relative_error_min} and < {thr.relative_error_max}",comp_err)
			else:return Compare2ValuesResults(SEVERITY_ERROR,f"Rel. err. > {thr.relative_error_max}",comp_err)
		else:
			err=abs(test-reference);comp_err=CompareFloatsErr(is_relative=_B,value=sign*err,test=test,reference=reference)
			if err<thr.absolute_error_max:
				if err>thr.absolute_error_min:return Compare2ValuesResults(SEVERITY_WARNING,f"Abs. err. > {thr.absolute_error_min} and < {thr.absolute_error_max}",comp_err)
			else:return Compare2ValuesResults(SEVERITY_ERROR,f"Abs. err. > {thr.absolute_error_max}",comp_err)
	def compare_dicts(self,test_dict,reference_dict,group):
		diffs_count=0;err_limit_reached=_B
		if set(test_dict.keys())!=set(reference_dict.keys()):raise Exception('Dictionaries have different keys')
		for key in test_dict:
			test_value=test_dict[key];reference_value=reference_dict[key];res_compare=self.compare_2_values(test_value,reference_value)
			if res_compare:err_limit_reached=self.compare_errors.add(group,res_compare,info={'key':key});diffs_count+=1;group.incr(_C)
			if err_limit_reached:break
		return err_limit_reached,diffs_count
	def compare_vectors(self,test_vector,reference_vector,group,info_vector=_A):
		B='ignore';A='RIAE_trapezoid'
		if len(test_vector)!=len(reference_vector):raise Exception('Vectors have different lengths')
		diffs_count=0;err_limit_reached=_B;ponderation_method=self.thresholds.vectors.ponderation_method if self.thresholds.vectors else _A
		if ponderation_method=='RIAE':ponderation_method=A
		if ponderation_method:logging.debug(f"Using ponderation method: {ponderation_method} with reduction_method {self.thresholds.vectors.reduction_method}")
		amplitude_compare=_A
		if self.thresholds.vectors and ponderation_method=='amplitude_moderation':amplitude=vector_get_amplitude(test_vector)[_D];amplitude_compare=amplitude*self.thresholds.vectors.amplitude_moderation_multiplier;reduction_method=self.thresholds.vectors.reduction_method
		RIAE_force_severity=_A
		if self.thresholds.vectors and ponderation_method in[A,'RIAE_midpoint']:
			if'CheckVectors'not in globals():raise Exception('scilens_compare not found. Please install scilens-compare package with `pip install scilens-compare`.')
			riae_error=CheckVectors.relative_integral_absolute_error_trapezoid(reference_vector,test_vector,range(len(test_vector)))if ponderation_method==A else CheckVectors.relative_integral_absolute_error_midpoint(reference_vector,test_vector,range(len(test_vector)))
			if riae_error is _A:logging.warning('RIAE calculation returned None. This may indicate an issue with the vectors.')
			else:
				RIAE_force_severity=self.thresholds.vectors.reduction_method
				if riae_error>self.thresholds.vectors.riae_threshold:ee=CompareFloatsErr(is_relative=_B,value=riae_error);res_compare=Compare2ValuesResults(SEVERITY_ERROR,f"RIAE ({ponderation_method}) > {self.thresholds.vectors.riae_threshold}",ee);err_limit_reached=self.compare_errors.add(group,res_compare)
		nb=len(test_vector)
		for idx in range(nb):
			diff=test_vector[idx]-reference_vector[idx]
			if diff==0:continue
			else:diffs_count+=1;group.incr(_C)
			if err_limit_reached:continue
			if RIAE_force_severity==B:continue
			if amplitude_compare is not _A and abs(diff)<amplitude_compare:
				if reduction_method==B:continue
				elif reduction_method=='soften':
					res_compare=self.compare_2_values(test_vector[idx],reference_vector[idx])
					if res_compare:res_compare.severity=SEVERITY_WARNING
			else:
				res_compare=self.compare_2_values(test_vector[idx],reference_vector[idx])
				if res_compare and RIAE_force_severity:res_compare.severity=SEVERITY_WARNING
			if res_compare:
				info={'index':idx}
				if info_vector:info['info']=info_vector[idx]
				err_limit_reached=self.compare_errors.add(group,res_compare,info=info)
		return err_limit_reached,diffs_count
	def add_group_and_compare_vectors(self,group_name,parent_group,group_data,test_vector,reference_vector,info_vector=_A):_,group=self.compare_errors.add_group('vectors',group_name,parent=parent_group,data=group_data);return(group,)+self.compare_vectors(test_vector,reference_vector,group,info_vector=info_vector)
	def compare_matrices(self,test_mat,ref_mat,group,x_vector=_A,y_vector=_A):
		diffs_count=0;err_limit_reached=_B;test_nb_lines=len(test_mat);test_nb_columns=len(test_mat[0])if test_nb_lines>0 else 0;ref_nb_lines=len(ref_mat);ref_nb_columns=len(ref_mat[0])if ref_nb_lines>0 else 0
		if test_nb_lines!=ref_nb_lines or test_nb_columns!=ref_nb_columns:raise Exception('Matrices have different dimensions')
		for i in range(test_nb_lines):
			for j in range(test_nb_columns):
				diff=test_mat[i][j]-ref_mat[i][j]
				if diff==0:continue
				else:diffs_count+=1;group.incr(_C)
				if err_limit_reached:continue
				res_compare=self.compare_2_values(test_mat[i][j],ref_mat[i][j])
				if res_compare:
					info={'i':i+1,'j':j+1}
					if x_vector:info['x']=x_vector[j]
					if y_vector:info['y']=y_vector[i]
					err_limit_reached=self.compare_errors.add(group,res_compare,info=info)
		return err_limit_reached,diffs_count
	def add_group_and_compare_matrices(self,group_name,parent_group,group_data,test_mat,ref_mat,x_vector=_A,y_vector=_A):_,group=self.compare_errors.add_group('matrix',group_name,parent=parent_group,data=group_data);return(group,)+self.compare_matrices(test_mat,ref_mat,group,x_vector=x_vector,y_vector=y_vector)