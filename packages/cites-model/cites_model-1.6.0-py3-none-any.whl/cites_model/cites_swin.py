from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field


class SingleWindowType(BaseModel):
    # Datová struktura pro čtení odpisů ze SWIN
    # TODO prověřit, zda se aktuálně používá
    version: Optional[str] = Field(default=None, description='Verze konektoru Single Window', examples=['writeoff:1.0.0.052'])
    transaction_list: Optional[List[Optional[str]]] = Field(
        default=None,
        description='Seznam odpisových transakcí',
        examples=['2f4cd677-33fb-4d17-8e7e-eaf4fe581422'])
    identifier_list: Optional[List[Optional[str]]] = Field(
        default=None,
        description='Seznam odpisových identifikátorů',
        examples=['2f4cd677-33fb-4d17-8e7e-eaf4fe581422'])
    change_json_list: Optional[List[Optional[str]]] = Field(default=None, description='Seznam odpisových změn v JSON')
    note: Optional[str] = Field(default=None, description='Poznámka')
