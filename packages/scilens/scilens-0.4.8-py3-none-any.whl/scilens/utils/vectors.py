def min_max_scaling(vector):
	A=vector;B=min(A);C=max(A)
	if C==B:return
	return[(A-B)/(C-B)for A in A]