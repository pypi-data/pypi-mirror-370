_A=None
from dataclasses import dataclass
from typing import Literal,Optional
from pydantic import BaseModel
SEVERITY_ERROR='error'
SEVERITY_WARNING='warning'
@dataclass
class CompareFloatsErr:is_relative:bool;value:float;test:float|_A=_A;reference:float|_A=_A
@dataclass
class Compare2ValuesResults:severity:str;message:str;comp_err:CompareFloatsErr|_A=_A
class CompareErr(BaseModel):err:CompareFloatsErr|_A;msg:int;group:int|_A=_A;info:dict|_A=_A
COMPARE_GROUP_TYPE=Literal['node','lines','vectors',' matrix','metrics','pixels']
@dataclass
class CompareGroup:
	id:int;type:COMPARE_GROUP_TYPE;name:str;parent:Optional['CompareGroup']=_A;error:str|_A=_A;total_diffs:int=0;total_warnings:int=0;total_errors:int=0;data:dict|_A=_A;info:dict|_A=_A
	def incr(A,type):
		if type==SEVERITY_ERROR:A.total_errors+=1
		elif type==SEVERITY_WARNING:A.total_warnings+=1
		elif type=='diff':A.total_diffs+=1
		if A.parent is not _A:A.parent.incr(type)