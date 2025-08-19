_A='yellow'
import rich_click as click
from scilens.app import pkg_name,pkg_version,pkg_homepage,pkg_documentations_url,powered_by
from scilens.utils.system import info as system_info
def echo_draw():click.echo(click.style("                           \n         :::::::::                         _____          _   _                                 \n       :::::::::::                        / ____|        (_) | |                           \n     ::       :::::::::::                | (___     ___   _  | |        ___   _ __    ___  \n   :::: :::::: :::::::::::::              \\___ \\   / __| | | | |       / _ \\ | '_ \\  / __|     \n   :::: ::::::  ::::::::::::::            ____) | | (__  | | | |____  |  __/ | | | | \\__ \\     \n  ::::::  :::  :::::::::::::::::         |_____/   \\___| |_| |______|  \\___| |_| |_| |___/     \n ::::::::::::::::::::::::::::::::       \n :::::::::::::::::::::::::::::::::      \n ::::::::::::::::::::::::::::::::::     \n                    :::::::::::::::     \n                      :::::::::::::     \n                       :::::::::::: \n               ::::    :::::::::::: \n             :::::::   :::::::::::  \n            ::::::::  :::::::::::   \n           ::::  ::  :::::::::::    \n           ::::::::::::::::::::     \n             :::::::::::::::        \n               ::::::::::           \n\n                                   \n",fg='magenta'))
def echo_info():
	B='blue';A='black';click.echo(pkg_name+' '+click.style(f"v{pkg_version}",fg=_A));click.echo(click.style('Visit ...........',fg=A)+' '+click.style(pkg_homepage,fg=B))
	if pkg_documentations_url:click.echo(click.style('Documentations ..',fg=A)+' '+click.style(pkg_documentations_url,fg=B))
	click.echo(click.style('Powered by ......',fg=A)+' '+click.style(powered_by['url'],fg=B))
def echo_system_info():
	A=system_info()
	for(B,C)in A.items():click.echo((B+' ').ljust(15,'.')+' '+click.style(f"{C}",fg=_A))