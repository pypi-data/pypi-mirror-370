from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import Field, BaseModel
from sysnet_pyutils.models.general import PersonBaseType, MetadataTypeBase, LinkedType, MetadataType

from cites_model.cites_common import BaseEntryListType, AdditionalEntryType, AdditionalTypeEnum, IssuingType, \
    GoodsIdetificationType, GoodsIdentificationChangeEnum, DiscardEnum, RelatedType, WorkflowListType


class CitesDocumentAdditionalEntryListType(BaseEntryListType):
    query: Optional[str] = Field(default=None, description='Dotaz na data', examples=['ftserach("luňák")'])
    entries: Optional[List[AdditionalEntryType]] = Field(default=None, description='Dotaz')


class CitesDocumentAdditionalTypeWrite(BaseModel):
    additional_type: Optional[AdditionalTypeEnum] = Field(
        default=None,
        description='Typ dodatečného dokumentu z číselníku',
        examples=['additionalRecord'],
    )
    date_delivered: Optional[datetime] = Field(
        default=None,
        description='datum doručení - DeliveredDate',
        examples=['2021-08-30T23:01:14.274085491+15:55'],
    )
    person_identifier: Optional[str] = Field(default=None, description='Identifikátor subjektu, který záznam pořídil')
    person_name: Optional[str] = Field(default=None, description='Název subjektu, který záznam pořídil')
    body: Optional[str] = Field(default=None, description='Obsah dodatečného dokumentu (např HTML)')
    issuing: Optional[IssuingType] = Field(default=None, description='Informace o vydání dokumentu')
    goods_identification_from: Optional[GoodsIdetificationType] = Field(default=None, description='Původní identifikace exempláře')
    goods_identification_to: Optional[GoodsIdetificationType] = Field(default=None, description='Nová identifikace exempláře')
    goods_identification_change: Optional[GoodsIdentificationChangeEnum] = Field(
        default=None,
        description='Typ změny identifikátoru (N - nový identifikátor, CH - změna identifikátoru, R - zrušení identifikátoru)\n',
        examples=['CH'],)
    holder_from: Optional[PersonBaseType] = Field(default=None, description='Původní držitel')
    holder_to: Optional[PersonBaseType] = Field(default=None, description='Nový držitel')
    date_checkout: Optional[datetime] = Field(
        default=None,
        description='Datum odhlášení',
        examples=['2021-08-30T23:01:14.274085491+15:55'],
    )
    date_sold: Optional[datetime] = Field(default=None, description='Datum prodeje', examples=['2021-08-30T23:01:14.274085491+15:55'])
    discard: Optional[DiscardEnum] = Field(default=None, description='důvod zrušení (D - úhyn, E - vývoz, OR - jiný důvod)')
    discard_comment: Optional[str] = Field(default=None, description='Komentář důvodu zrušení')
    original_document_returned: Optional[bool] = Field(default=None, description='Originál dokladu vrácen', examples=[False])
    note: Optional[str] = Field(default=None, description='Poznámky')
    status: Optional[str] = Field(default=None, description='Stavová informace')
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Zapisovaná metadata')
    parent: Optional[RelatedType] = Field(default=None, description='Rodičovský dokument')
    workflow: Optional[WorkflowListType] = Field(default=None, description='Historie životního cyklu')
    linked_list: Optional[List[Optional[LinkedType]]] = Field(default=None, description='Seznam provázaných dat')


class CitesDocumentAdditionalType(CitesDocumentAdditionalTypeWrite):
    doc_code: str = Field(
        default=None,
        description='Kód dokumentu z číselníku - vazba na formuláře PDF',
        examples=['DD01'],
    )
    metadata: Optional[MetadataType] = Field(default=None, description='Kompletní metadata')
    history: Optional[List[Optional[str]]] = Field(default=None, description='Historie dokumentu ($History)')

