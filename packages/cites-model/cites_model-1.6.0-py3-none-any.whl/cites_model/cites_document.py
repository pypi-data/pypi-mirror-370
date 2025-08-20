from __future__ import annotations

from typing import Optional, List, Union

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import MetadataTypeBase, LinkedType, MetadataType

from cites_model.cites_common import GeneralType, TransactionType, ConditionsType, IssuingType, OtherType, \
    PermitSpecialConditionsType, DocumentPrincipalCustomsPermitType, GoodsPrincipalType, WorkflowListType, \
    BaseEntryListType, EntryType, GoodsPrincipalTypeWrite


class CitesDocumentEntryListType(BaseEntryListType):
    query: Optional[str] = Field(default=None, description='Dotaz na data', examples=['ftserach("luňák")'])
    entries: Optional[List[Optional[EntryType]]] = Field(default=None, description='Položky seznamu')


class CitesDocumentPrincipalTypeWrite(BaseModel):
    doc_code: Optional[str] = Field(default=None, description='Kód dokumentu - vazba na šablony', examples=['DD01'])
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Zapisovaná metadata')
    document: Optional[GeneralType] = Field(default=None, description='Základní data dokumentu')
    transaction: Optional[List[Optional[TransactionType]]] = Field(default=None, description='Seznam transakčních údajů')
    conditions: Optional[ConditionsType] = Field(default=None, description='Podmínky vydání dokumentu')
    issuing: Optional[IssuingType] = Field(default=None, description='Vydavatel')
    other: Optional[OtherType] = Field(default=None, description='Další údaje')
    permit_conditions: Optional[PermitSpecialConditionsType] = Field(default=None, description='Podmínky permitu')
    customs: Optional[DocumentPrincipalCustomsPermitType] = Field(default=None, description='Celní údaje permitu')
    goods: Optional[List[Optional[GoodsPrincipalTypeWrite]]] = Field(default=None, description='Seznam zboží')
    note: Optional[str] = Field(default=None, description='Poznámky')
    comment: Optional[str] = Field(default=None, description='Obecná poznámka')
    workflow: Optional[WorkflowListType] = Field(default=None, description='Historie životního cyklu')
    linked_list: Optional[List[Optional[LinkedType]]] = Field(default=None, description='Seznam provázaných dat')

    def get_goods_by_order(self, order: Union[int, str] = 1) -> Optional[GoodsPrincipalType]:
        if order is None:
            return None
        if self.goods:
            if isinstance(order, str):
                try:
                    order = int(order)
                except ValueError:
                    pass
            for good in self.goods:
                if isinstance(order, int):
                    if good.order.num_value == order:
                        return good
                elif isinstance(order, str):
                    if good.order.text_value == order:
                        return good
        return None

class CitesDocumentPrincipalType(CitesDocumentPrincipalTypeWrite):
    metadata: Optional[MetadataType] = Field(default=None, description='Úplná metadata')
    goods: Optional[List[Optional[GoodsPrincipalType]]] = Field(default=None, description='Seznam zboží')
    history: Optional[List[Optional[str]]] = Field(default=None, description='Historie dokumentu ($History)')

    @property
    def purpose_traces(self):
        # Účel pro Traces. Použije se účel prvního zboží
        if self.goods:
            out = self.goods[0].purpose
            return out
        return None

    @property
    def token(self):
        # Token pro výměnný model
        out = self.metadata.pid
        if self.document.permit_token not in ['', None] and isinstance(self.document.permit_token, str):
            out = self.document.permit_token
        return out
