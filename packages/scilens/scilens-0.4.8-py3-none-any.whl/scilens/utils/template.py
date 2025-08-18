from jinja2 import Template,Environment,FileSystemLoader
def template_render_string(template_str,context):return Template(template_str).render(context)
def template_render_path(filepath,context):
	with open(filepath,'r')as A:B=A.read();return template_render_string(B,context)
def template_render_infolder(filename,context,template_dir):A=FileSystemLoader([template_dir]);B=Environment(loader=A);return B.get_template(filename).render(context)