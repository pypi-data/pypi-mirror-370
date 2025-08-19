import types,pydantic
class StrOrPath(str):
	@classmethod
	def __get_pydantic_core_schema__(A,source_type,handler):return handler(str)
	def __repr__(A):return f"{A.__class__.__name__}({super().__repr__()})"
def is_StrOrPath_and_path(value,field_info):
	D=False;B=field_info;A=value;C='file://'
	if not isinstance(A,str):return D,''
	if B.annotation==StrOrPath or isinstance(B.annotation,types.UnionType)and StrOrPath in B.annotation.__args__:
		if A.startswith(C):return True,A[len(C):]
	return D,''