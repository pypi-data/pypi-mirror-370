_A=None
from pydantic import BaseModel,Field
from scilens.config.models.execute import ExecuteConfig
class ExecuteAndCompareConfig(BaseModel,extra='forbid'):test:ExecuteConfig|_A=Field(default=_A,description='Surcharge les paramètres de la section `execute` pour le contexte de test.');test_only:bool=Field(default=False,description='Si `true`, aucune éxécution faite pour la référence (les sorties de réferences pour comparaison existent déjà).');reference:ExecuteConfig|_A=Field(default=_A,description='Surcharge les paramètres de la section `execute` pour le contexte de référence.')