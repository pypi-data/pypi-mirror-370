from pydantic import BaseModel
class ProcessorResults(BaseModel):data:list=[];errors:list[str]=[];warnings:list[str]=[]