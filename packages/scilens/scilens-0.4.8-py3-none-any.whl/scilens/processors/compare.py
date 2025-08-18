import logging
from scilens.processors.models.results import ProcessorResults
from scilens.run.task_context import TaskContext
from scilens.components.compare_folders import CompareFolders
class Compare:
	def __init__(A,context):B=context;A.context=B;A.compare_folders=CompareFolders(B)
	def process(B):E='error';A=ProcessorResults();C=B.compare_folders.compute_list_filenames();logging.info(f"Number files to compare: {len(C)}");D=B.compare_folders.compute_comparison(C);A.warnings=[A[E]for A in D if A.get(E)];A.data=D;return A