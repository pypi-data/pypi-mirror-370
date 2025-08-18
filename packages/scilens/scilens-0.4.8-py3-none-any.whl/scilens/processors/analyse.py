import logging
from scilens.processors.models.results import ProcessorResults
from scilens.readers.reader_manager import ReaderManager
from scilens.run.task_context import TaskContext
from scilens.components.analyse_folder import AnalyseFolder
class Analyse:
	def __init__(A,context):A.context=context
	def process(A):
		logging.info('Listing files to process');B=AnalyseFolder().get_list_dir(A.context.working_dir,exclude_files=[A.context.config_file]if A.context.config_file else None);logging.info(f"Number of files to process: {len(B)}");logging.info(f"Files to process: {B}")
		for C in B:
			logging.info(f"Processing file: {C}");D=ReaderManager().get_reader_from_file(C)
			if not D:logging.warning(f"Reader not found for file: {C}");continue
			logging.info(f"Reader: {D.__class__.__name__}")
		return ProcessorResults()