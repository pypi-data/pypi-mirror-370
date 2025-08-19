_B='green'
_A=True
import logging,os,webbrowser,coloredlogs,rich_click as click
from scilens.app import pkg_name,pkg_version
from scilens.readers.reader_manager import ReaderManager
from scilens.run.tasks_collector import TasksCollector
from scilens.run.models.task_results import TaskResults
from scilens.utils.time_tracker import TimeTracker
from scilens.cli.config import config_print
from scilens.cli.cglb import cglb_process
from scilens.cli.info import echo_info,echo_system_info,echo_draw
from scilens.config.cli_run_options import get_vars
from scilens.helpers.search_and_index import SearchAndIndex
def echo_separator(msg=None):
	A=msg
	if A:A=f" {A}";click.echo(click.style(A.rjust(80,'='),fg=_B))
	else:click.echo(click.style('='*80,fg=_B))
def echo_task_error():click.echo(click.style('='*80,fg='red'))
@click.group()
@click.option('--log-level',default='INFO',help='Log level. Default is INFO. Available levels are DEBUG, INFO, WARNING, ERROR, CRITICAL.')
def cli(log_level):coloredlogs.install(level=log_level)
@cli.command(short_help='Show the version information')
def version():click.echo(f"{pkg_name} v{pkg_version}")
@cli.command(short_help='CesGensLaB Slogan',hidden=_A)
def cesgenslab():cglb_process()
@cli.command(short_help='Show application informations')
def info():echo_draw();echo_info()
@cli.command(short_help='Show system informations. (Useful for dynamic context configuration)')
def sysinfo():echo_system_info()
@cli.command(short_help='Show the reader plugins')
def readers():
	J='configuration_type_code';I='class';D='yellow';A=' ';C=ReaderManager()._get_plugin_info();E='Class';F='Configuration Type Code';B=max([len(A[I])for A in C]+[len(E)]);G=max([len(A[J])for A in C]+[len(F)]);click.echo(click.style((E+A).ljust(B,A),fg=_B)+A+click.style(F,fg=D));click.echo(click.style(('-'*B).ljust(B,A),fg=_B)+A+click.style('-'*G,fg=D))
	for H in C:click.echo(click.style(H[I].ljust(B,A),fg=_B)+A+click.style(H[J].ljust(G,A),fg=D))
@cli.group()
def config():0
@config.command(name='default',short_help='Example of default config')
def config_default():config_print('yaml')
@config.command(name='json',short_help='Show the config structure in json schema format')
def config_json():config_print('json')
@config.command(name='envvar',short_help='Show the available environment variables')
def config_json():config_print('envvars')
@cli.command(short_help='Run data collections and analysis')
@click.argument('path',required=_A)
@click.option('--config',help=f'Path to the yaml test configuration file. If not provided, search for a file named "{pkg_name}.yml" in the PATH (exlusive with --processor, --collect-depth and --collect-discover).')
@click.option('--collect-discover',is_flag=_A,help=f'Explore recursively PATH seeking for "{pkg_name}.yml" configuration files, and run them sequentially (exlusive with --config and --processor and --collect-depth).')
@click.option('--collect-depth',type=int,help=f'Walk the PATH and list subdirectories at depth --collect-depth." (exlusive with --config, --processor and --collect-discover).')
@click.option('--processor',help=f"If specified, run with this processor, default configuration values, and environment variables (exlusive with --config, --collect-depth and --collect-discover).")
@click.option('--tag',multiple=_A,help=f'Filter collected tasks on tags defined in corresponding "{pkg_name}.yml". (Can be used multiple times).')
@click.option('--collect-only',is_flag=_A,help=f"Collect only, with --discover or not. Do not run the tasks.")
@click.option('--report-title',help=f"Define report title.")
@click.option('--export-html',is_flag=_A,help=f"Generate HTML report(s).")
@click.option('--export-json',is_flag=_A,help=f"Generate JSON report(s).")
@click.option('--export-yaml',is_flag=_A,help=f"Generate YAML report(s).")
@click.option('--export-html-add-index',is_flag=_A,help=f"Generate an index for generated HTML reports.")
@click.option('--export-html-open',is_flag=_A,help=f"Open all generated HTML reports in the default browser.")
def run(path,config,collect_discover,collect_depth,processor,tag,collect_only,report_title,export_html,export_json,export_yaml,export_html_add_index,export_html_open):
	V='datetime';M=export_html_open;L=export_html_add_index;K=processor;J=collect_discover;I=config;E=collect_depth;echo_separator('Info');echo_info();echo_separator('System Info');echo_system_info();W=list(tag);B=os.path.abspath(path)
	if not os.path.isdir(B):logging.error(f"Dir '{B}' does not exist.");exit(1)
	if not bool(I)+J+(bool(E)or E==0)+bool(K)in[0,1]:logging.error(f"Options --config, --collect-discover, --collect-depth and --processor are mutually exclusive.");exit(1)
	echo_separator('Collecting tasks');F=[]
	try:F=TasksCollector(B,I,J,E,W,K).process(get_vars(report_title,export_html,export_json,export_yaml))
	except Exception as D:logging.error(D);exit(1)
	if collect_only:echo_separator();logging.info('Collecting tasks only - End');echo_separator();exit(0)
	else:
		N=TimeTracker();A=len(F);O=0;P=0;Q=0;R=[]
		for(X,Y)in enumerate(F):
			echo_separator(f"Running task {X+1}/{A}")
			try:C=Y.process()
			except Exception as D:echo_task_error();logging.error(D);C=TaskResults(error=str(D))
			if C.report_results:R+=C.report_results.files_created
			if C.error:O+=1
			G=C.processor_results
			if G:
				if G.warnings:Q+=1
				if G.errors:P+=1
		if L or M:
			echo_separator(f"Post Actions");S=[A for A in R if A.endswith('.html')]
			if L:logging.info(f"Generate HTML Index for the HTML reports");T=os.path.join(B,'index.html');SearchAndIndex().create_html_index(SearchAndIndex().file_list_info_from_origin(S,B),T,title='Index of Reports');logging.info(f"HTML Index generated at '{T}'")
			if M:
				logging.info(f"Open HTML reports in the default browser")
				for U in S:logging.info(f"Open '{U}'");Z=f"file://{U}";webbrowser.open(Z)
		echo_separator(f"End Running tasks ({A}/{A})");N.stop();H=N.get_data();logging.info(f"Tasks with errors ............... {O}/{A}");logging.info(f"Tasks with processor errors ..... {P}/{A}");logging.info(f"Tasks with processor warnings ... {Q}/{A}");logging.info(f"Start ........................... {H['start'][V]} utc");logging.info(f"End ............................. {H['end'][V]} utc");logging.info(f"Duration......................... {H['duration_seconds']} seconds");echo_separator()