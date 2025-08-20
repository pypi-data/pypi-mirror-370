from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field

from cites_model.cites_common import (
    AdditionalType, HybridType, Regulation449Enum, RegulationCitesEnum, RegulationEuEnum)


class TaxonEntryType(BaseModel):
    pid: Optional[str] = Field(default=None, description='Identifikátor Registru CITES', examples=['EAP785A1SFJV'])
    pid_main: Optional[str] = Field(default=None, description='Pokud je taxon duplicitou, toto pole obsahuje PID hlavního taxonu', examples=['EAP785A1SFJV'])
    is_duplicity: Optional[bool] = Field(default=None, description='Indikátor duplicity', examples=[False])
    is_hybrid: Optional[bool] = Field(default=None, description='Indikátor křížence', examples=[False])
    name_common_cz: Optional[str] = Field(default=None, description='Obecný název (česky)', examples=['luňákovec kubánský'])
    name_common_en: Optional[str] = Field(default=None, description='Obecný název (anglicky)', examples=['Cuban Hook-billed Kite'])
    name_scientific: str = Field(default=None, description='Vědecký název (latinsky)', examples=['Chondrohierax uncinatus wilsonii'])
    regulation_cites: Optional[RegulationCitesEnum] = Field(default=None, description='Exemplář sledovaný podle CI=TES', examples=[RegulationCitesEnum.I])
    regulation_eu: Optional[RegulationEuEnum] = Field(default=None, description='Exemplář sledovaný podle EU', examples=[RegulationEuEnum.A])


class TaxonType(TaxonEntryType):
    id_species_plus: Optional[List[str]] = Field(default=None, description='Identifikátor species+')
    name_listed: Optional[str] = Field(default=None, description='listed_under (species+)', examples=['Chondrohierax uncinatus wilsonii'])
    rank_regnum: Optional[str] = Field(default=None, description='Říše', examples=['Animalia'])
    rank_phylum: Optional[str] = Field(default=None, description='Kmen', examples=['Chordata'])
    rank_divisio: Optional[str] = Field(default=None, description='Oddělení (pro botaniku)')
    rank_classis: Optional[str] = Field(default=None, description='Třída', examples=['Aves'])
    rank_ordo: Optional[str] = Field(default=None, description='Řád', examples=['Falconiformes'])
    rank_familia: Optional[str] = Field(default=None, description='Čeleď', examples=['Accipitridae'])
    rank_genus: Optional[str] = Field(default=None, description='Rod', examples=['Chondrohierax'])
    rank_species: Optional[str] = Field(default=None, description='Druh', examples=['uncinatus'])
    rank_subspecies: Optional[str] = Field(default=None, description='Poddruh', examples=['wilsonii'])
    rank_varietas: Optional[str] = Field(default=None, description='Varieta', examples=['ampanihyensis'])
    rank: Optional[str] = Field(default=None, description='Nejnižší taxonomické rozlišení položky (SPECIES, SUBSPECIES, VARIETY)', examples=['SPECIES'])
    rank_hybrid: Optional[str] = Field(default=None, description='Kříženec')
    regulation_102: Optional[bool] = Field(default=None, description='Exemplář sledovaný podle zákona č. 102/19963 Sb. (rybářství)', examples=[False])
    regulation_114: Optional[str] = Field(default=None, description='Exemplář sledovaný podle zákona č. 114/1997 Sb. (ochrana přírody)', examples=['KO'])
    regulation_411: Optional[bool] = Field(default=None, description='Exemplář sledovaný podle vyhlášky č. 411/2008 Sb., kterou se stanoví druhy zvířat vyžadující zvláštní péči', examples=[False])
    regulation_449: Optional[Regulation449Enum] = Field(default=None, description='Exemplář sledovaný podle zákona 449 (myslivost)', examples=['A'])
    regulation_95: Optional[bool] = Field(default=None, description='Exemplář sledovaný podle vyhláška č. 95/1996 Sb. (nebezpečná zvířata)', examples=[False])
    synonyms: Optional[List[str]] = Field(default=None, description='variantní vědecké názvy pro stejný taxon')
    is_valid: Optional[bool] = Field(default=None, description='je taxon validní?', examples=[True])
    is_published: Optional[bool] = Field(default=None, description='je taxon publikován v našeptávačích?', examples=[True])
    is_deleted: Optional[bool] = Field(default=None, description='je taxon odstraněn?', examples=[False])
    is_active: Optional[bool] = Field(default=None, description='Indikátor aktivního použití na webu', examples=[False])
    hybrid: Optional[HybridType] = Field(default=None, description='popis krížence')
    additional: Optional[AdditionalType] = Field(default=None, description='dodatečná informace')


class TaxonEntryListType(BaseModel):
    key: Optional[str] = Field(default=None, description='Textový klíč (např. species)', examples=['luňák'])
    start: Optional[int] = Field(default=None, description='Počáteční dokument na stránce', examples=[0])
    page_size: Optional[int] = Field(default=None, description='Velikost stránky', examples=[10])
    page: Optional[int] = Field(default=None, description='Požadovaná stránka', examples=[0])
    count: Optional[int] = Field(default=None, description='počet vrácených položek', examples=[10])
    hits: Optional[int] = Field(default=None, description='celkový počet vrácených položek', examples=[2587])
    entries: Optional[List[TaxonEntryType]] = None

