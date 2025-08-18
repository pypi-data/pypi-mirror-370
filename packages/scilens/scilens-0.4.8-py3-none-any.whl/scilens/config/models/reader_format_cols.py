_C='(Valide seulement si la première ligne est les en-têtes)'
_B='forbid'
_A=None
from pydantic import BaseModel,Field,model_validator
from enum import Enum
class ReaderCurveParserNameConfig(str,Enum):COL_X='col_x';COLS_COUPLE='cols_couple'
class ReaderCurveParserColXConfig(BaseModel,extra=_B):x:int|str|list[str]=Field(default=1,description="Si `integer`, index de la colonne pour l'axe x (index `1` pour la première colonne)."+"Si `String`, nom de la colonne pour l'axe x. Si la colonne n'existe pas, il n'y aura pas de parsing."+_C+"Si `List[String] (utiles dans un contexte multi dataset), noms de la colonne pour l'axe x, noms des colonnes pour l'axe x , si plusieurs colonnes correspondent, la première trouvée sera utilisée. Si aucune colonne ne correspond, il n'y aura pas de parsing."+_C)
class ReaderCurveParserColsCoupleConfig(BaseModel,extra=_B):x_index:int=Field(description='NOT IMPLEMENTED - Index Col x');y_index:int=Field(description='NOT IMPLEMENTED - Index Col y')
class ReaderColsCurveParserConfig(BaseModel,extra=_B):
	name:ReaderCurveParserNameConfig=Field(description='Le type de `paramètres` dépend de cette valeur');parameters:ReaderCurveParserColXConfig|ReaderCurveParserColsCoupleConfig|_A=Field(default=_A,description='Paramètres du parser de courbes')
	@model_validator(mode='after')
	def validate_model(cls,model):
		A=model
		if isinstance(A.parameters,ReaderCurveParserColXConfig)and A.name!=ReaderCurveParserNameConfig.COL_X or isinstance(A.parameters,ReaderCurveParserColsCoupleConfig)and A.name!=ReaderCurveParserNameConfig.COLS_COUPLE:raise ValueError(f"Curve Parser {A.name} Parameters are not correct")
		if isinstance(A.parameters,dict):
			if A.name==ReaderCurveParserNameConfig.COL_X:A.parameters=ReaderCurveParserColXConfig(**A.parameters)
			elif A.name==ReaderCurveParserNameConfig.COLS_COUPLE:A.parameters=ReaderCurveParserColsCoupleConfig(**A.parameters)
		return A
class ReaderColsRowsConfig(BaseModel,extra=_B):ignore_patterns:list[str]|_A=Field(default=_A,description='Liste des patterns de lignes à ignorer. Ex: ["^#", "^//"]. Non applicable si `is_matrix` est vrai.');line_start:int|_A=Field(default=_A,description='Ligne de début pour lire le fichier (les en-têtes sont comptées comme une ligne). Si non défini, commence à la première ligne.');line_end:int|_A=Field(default=_A,description="Ligne de fin pour lire le fichier (les en-têtes sont comptées comme une ligne). Si non défini, lit jusqu'à la dernière ligne.");index_min_value:float|_A=Field(default=_A,description="Valeur minimale de l'index pour les lignes à lire (valeur incluses).");index_max_value:float|_A=Field(default=_A,description="Valeur maximale de l'index pour les lignes à lire (valeur incluses).")
class ReaderColsConfig(BaseModel,extra=_B):ignore_columns:list[str]|list[int]|_A=Field(default=_A,description="Liste des colonnes à ignorer (nom de l'en tête ou numéro de colonne).");index_col:int|str|list[str]|_A=Field(default=_A,description='Colonne(s) à utiliser comme index (date/heure, itération, étape, ...) (Utilisé dans différentes règles). Numéro de colonne ou nom(s) de colonne. (Valide seulement si non matrice)');rows:ReaderColsRowsConfig|_A=Field(default=_A,description='Configuration des lignes à lire.');curve_parser:ReaderColsCurveParserConfig|_A=Field(default=_A,description='Parseur de courbe à utiliser.')