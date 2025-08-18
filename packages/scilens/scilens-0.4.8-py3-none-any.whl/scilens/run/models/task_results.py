_A=None
from pydantic import BaseModel
from scilens.processors.models.results import ProcessorResults
from scilens.report.report import ReportProcessResults
class TaskResults(BaseModel):error:str|_A=_A;processor_results:ProcessorResults|_A=_A;report_results:ReportProcessResults|_A=_A