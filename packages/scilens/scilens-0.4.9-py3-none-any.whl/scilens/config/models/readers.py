_A='forbid'
from typing import Literal
from pydantic import BaseModel,Field
from scilens.config.models.reader_format_txt import ReaderTxtConfig
from scilens.config.models.reader_format_csv import ReaderCsvConfig
from scilens.config.models.reader_format_txt_fixed_cols import ReaderTxtFixedColsConfig
from scilens.config.models.reader_format_netcdf import ReaderNetcdfConfig
class BaseCatalogItem(BaseModel,extra=_A):type:str
class ReaderTxtConfigItem(BaseCatalogItem,extra=_A):type:Literal['txt'];parameters:ReaderTxtConfig
class ReaderCsvConfigItem(BaseCatalogItem,extra=_A):type:Literal['csv'];parameters:ReaderCsvConfig
class ReaderTxtFixedColsConfigItem(BaseCatalogItem,extra=_A):type:Literal['txt_fixed_cols'];parameters:ReaderTxtFixedColsConfig
class ReaderNetcdfConfigItem(BaseCatalogItem,extra=_A):type:Literal['netcdf'];parameters:ReaderNetcdfConfig
CATALOG_ITEM_TYPE=ReaderTxtConfigItem|ReaderCsvConfigItem|ReaderTxtFixedColsConfigItem|ReaderNetcdfConfigItem
class ReadersConfig(BaseModel,extra=_A):txt:ReaderTxtConfig=Field(default=ReaderTxtConfig(),description='Configuration des readers txt.');csv:ReaderCsvConfig=Field(default=ReaderCsvConfig(),description='Configuration des readers csv.');txt_fixed_cols:ReaderTxtFixedColsConfig=Field(default=ReaderTxtFixedColsConfig(),description='Configuration des readers txt avec colonnes fixes.');netcdf:ReaderNetcdfConfig=Field(default=ReaderNetcdfConfig(),description='Configuration des readers NetCDF.');catalog:dict[str,CATALOG_ITEM_TYPE]|None=Field(default=None,description="Catalogue de configuration de readers par clé. Ex: `{'csv_comma': {'type': 'csv', 'parameters': {'delimiter': ','}}, 'csv_semicolon': {'type': 'csv', 'parameters': {'delimiter': ';'}}}`")