import platform,sys
def info():A=sys.version_info;return{'os':platform.system().lower(),'arch':platform.machine(),'python':f"{A.major}.{A.minor}.{A.micro}",'python_info':sys.version}