_A=False
def get_vars(title='',export_html=_A,export_json=_A,export_yaml=_A):
	C=title;B=True;A={}
	if C:A['report.title']=C
	if export_html:A['report.output.export_html']=B
	if export_json:A['report.output.export_json']=B
	if export_yaml:A['report.output.export_yaml']=B
	return A