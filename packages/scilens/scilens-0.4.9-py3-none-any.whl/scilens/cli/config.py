import json,click
from rich.console import Console
from rich.syntax import Syntax
from scilens.app import pkg_name,pkg_version
from scilens.config.models import AppConfig
from scilens.config.load import pydantic_to_yaml
from scilens.config.env_var import get_vars
console=Console()
def config_print(mode):
	H='green';G='json';F='yaml';B=mode;A=' '
	if B==F:I=pydantic_to_yaml(AppConfig(processor='processor'));C=Syntax(I,F,line_numbers=True);console.print();console.rule(f"[bold green]{pkg_name}.yml[/bold green]");console.print(C)
	if B==G:J=AppConfig.model_json_schema();C=Syntax(json.dumps(J,indent=2),G,line_numbers=True);console.print(C)
	if B=='envvars':
		D=get_vars();E=max([len(A)for A in D])+4;K=max([len(A)for A in D.values()])+4;click.echo(click.style(('Environment variable name'+A).ljust(E,A)+A+'Config variable path',fg=H));click.echo(click.style('='*E+A+'='*K,fg=H))
		for(L,M)in D.items():click.echo(click.style((L+A).ljust(E,'.'),fg='yellow')+A+M)