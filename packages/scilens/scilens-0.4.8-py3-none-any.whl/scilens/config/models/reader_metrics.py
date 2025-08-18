_C='Nom de la métrique.'
_B='forbid'
_A=None
from pydantic import BaseModel,Field
class ReaderTxtMetricsConfig(BaseModel,extra=_B):name:str|_A=Field(default=_A,description=_C);pattern:str=Field(default=_A,description='Expression régulière pour identifier la métrique.');number_position:int=Field(default=1,description='Position du nombre dans le tableau de nombres de la ligne.')
class ReaderColsMetricsConfig(BaseModel,extra=_B):name:str|_A=Field(default=_A,description=_C);aggregation:str=Field(default='sum',description="Méthode d'agrégation du vecteur `col` ou du vecteur résultat de la `function`. Peut être `mean`, `sum`, `min`, `max`.");col:int|str|_A=Field(default=_A,description='Colonnes (index ou noms) de la métrique.');function:str|_A=Field(default=_A,description="Fonction norme de l'espace vectoriel . Peut être `euclidean_norm`.");components:list[int]|list[str]|_A=Field(default=_A,description='Colonnes (index ou noms) de la `function`.')