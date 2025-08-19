import time,rich_click as click
from rich.console import Console
from rich.progress import Progress
def cglb_process():
	B='results';A='command';G=Console();E=[{A:'dev',B:'better'},{A:'build',B:'bigger'},{A:'run',B:'faster'}]
	for C in E:
		with Progress()as D:
			F=D.add_task(f"[cyan]{C[A]}".ljust(20,'-'),total=10)
			for H in range(10):time.sleep(.1);D.update(F,advance=1)
		click.echo(click.style(' => '+C[B].upper()+' !\n',fg='magenta'))