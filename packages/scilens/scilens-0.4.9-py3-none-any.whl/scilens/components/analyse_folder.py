import os
class AnalyseFolder:
	def __init__(A):0
	def get_list_dir(C,dir,exclude_files=None):A=exclude_files;B=[os.path.join(dir,A)for A in os.listdir(dir)];return B if not A else[B for B in B if B not in A]