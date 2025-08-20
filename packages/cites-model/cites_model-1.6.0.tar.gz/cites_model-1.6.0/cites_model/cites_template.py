from typing import Optional

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import BaseEnum


class TemplateTypeEnum(BaseEnum):
    PDF = 'PDF'
    JASPER = 'JASPER'
    HTMS = 'HTML'
    EMPTY = ''
    NULL = None


class TemplateBaseType(BaseModel):
    doc_code: Optional[str] = Field(
        default=None,
        description='Kód dokumentu z číselníku - vazba na formuláře PDF',
        examples=['DD01'],
    )
    name: Optional[str] = Field(default=None, description='Název šablony')
    form: Optional[str] = Field(default=None, description='Název formuláře')
    form_pdf: Optional[str] = Field(default=None, description='Název formuláře v šabloně PDF')
    template_type: Optional[TemplateTypeEnum] = Field(default=TemplateTypeEnum.PDF, description='typ šablony')
    has_enclosure: Optional[bool] = Field(default=False, description='dokument může mít přílohy v jiném formuláři')
    enclosure_size: Optional[int] = Field(default=0, description='počet položek na příloze')
    comment: Optional[str] = Field(default=None, description='Obecná poznámka')


class TemplateFullType(TemplateBaseType):
    template_first: Optional[str] = Field(
        default=None,
        description='Nazev souboru šablony první stránky',
        examples=['file1.pdf']
    )
    template_enclosure: Optional[str] = Field(
        default=None,
        description='Nazev souboru šablony přílohy',
        examples=['file2.pdf']
    )
