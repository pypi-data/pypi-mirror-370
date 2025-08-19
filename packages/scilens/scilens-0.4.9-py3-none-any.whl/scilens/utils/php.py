def dict_to_php_array(data,indent=0):
	F='array(\n';D=indent;B=data;A='';C=' '*(D*4)
	if isinstance(B,dict):
		A+=F
		for(G,E)in B.items():A+=f"{C}    '{G}' => {dict_to_php_array(E,D+1)},\n"
		A+=f"{C})"
	elif isinstance(B,list):
		A+=F
		for E in B:A+=f"{C}    {dict_to_php_array(E,D+1)},\n"
		A+=f"{C})"
	elif isinstance(B,str):A+=f"'{B}'"
	elif isinstance(B,bool):A+='true'if B else'false'
	elif B is None:A+='null'
	else:A+=str(B)
	return A