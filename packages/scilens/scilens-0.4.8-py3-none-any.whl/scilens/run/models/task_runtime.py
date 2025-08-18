from pydantic import BaseModel
class TaskRuntime(BaseModel):sys:dict[str,str];env:dict[str,str];vars:dict[str,str]