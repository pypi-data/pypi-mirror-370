_A='Configuration utile au processeur `ExecuteAndCompare`.'
from pydantic import BaseModel,Field
from scilens.config.models.compare import CompareConfig
from scilens.config.models.execute import ExecuteConfig
from scilens.config.models.execute_and_compare import ExecuteAndCompareConfig
from scilens.config.models.file_reader import FileReaderConfig
from scilens.config.models.readers import ReadersConfig
from scilens.config.models.report import ReportConfig
class AppConfig(BaseModel,extra='forbid'):processor:str=Field(description='Nom du processeur à utiliser. `Compare` ou `ExecuteAndCompare`.');variables:dict[str,str]=Field(default={},description='Variables Utilisateur.');tags:list[str]|None=Field(default=None,description="Utilisé dans un contexte ligne de commande, utilisé en conjonction avec l'option `--discover` pour filtrer les cas à éxécuter.");execute:ExecuteConfig=Field(default=ExecuteConfig(),description=_A);execute_and_compare:ExecuteAndCompareConfig=Field(default=ExecuteAndCompareConfig(),description=_A);file_reader:FileReaderConfig=Field(default=FileReaderConfig(),description='Configuration des readers fichiers.');readers:ReadersConfig=Field(default=ReadersConfig(),description='Configuration des readers.');compare:CompareConfig=Field(default=CompareConfig(),description='Configuration utile aux processeurs `Compare` et `ExecuteAndCompare`');report:ReportConfig=Field(default=ReportConfig(),description='Configuration des Reports.')