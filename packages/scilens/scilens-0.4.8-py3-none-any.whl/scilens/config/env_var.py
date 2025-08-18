from scilens.app import pkg_name
ENV_VARS_CONFIG_MODEL=['processor','execute.command_suffix','execute_and_compare.test.exe_path','execute_and_compare.reference.exe_path','report.title']
def get_vars():return{f"{pkg_name.upper()}_{A.upper().replace('.','_')}":A for A in ENV_VARS_CONFIG_MODEL}