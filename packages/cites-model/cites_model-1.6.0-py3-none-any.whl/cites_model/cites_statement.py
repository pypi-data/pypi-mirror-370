from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from cites_model.cites_common import (
    GoodsItemBaseType, WorkflowListType, PersonExtendedType, TaxonItemType, RelatedType, IssuingType,
    GoodsIdetificationType, GoodsBirthType, BirthTypeEnum, TransactionType, GoodsQuantityType, MetricEnum,
    ExceptionTypeEnum, IntentEnum, AgreeType)
from pydantic import Field, BaseModel
from sysnet_pyutils.data_utils import get_dict_value_int, get_dict_value, get_dict_item_value_list
from sysnet_pyutils.models.general import MetadataType, LinkedType, MetadataTypeBase, BaseEnum, LogItemType



class StatementTypeEnum(BaseEnum):
    PERMIT = 'permit'
    CERTIFICATE = 'certificate'


class SpecimenParentType(GoodsItemBaseType):
    # Rodičovský exemplář položky žádosti o stanovisko k výjimce
    note: Optional[str] = Field(default=None, description='Poznámka')
    reference_list: Optional[List[str]] = Field(
        default=None,
        description='Seznam čísel registračních listů',
        examples=['PHA/00951/2020', 'PHA/00953/2020'],
        min_length=0,
    )
    certificate_list: Optional[List[str]] = Field(
        default=None,
        description='Seznam čísel potvrzení o výjimkách',
        examples=['CZ/PAK/00236/2017'],
        min_length=0,
    )
    acquisition: Optional[str] = Field(default=None, description='Způsob získání')


class SpecimenType(GoodsItemBaseType):
    # Exemplář v žádosti o stanovisko k výjimce
    identifier: Optional[str] = Field(
        default=None,
        description='identifikátor položky',
        examples=['9d6e2fc9-ca1f-4504-a54b-c8263a21c678'],
    )
    pid: Optional[str] = Field(
        default=None,
        description='identifikátor položky',
    )
    unid: Optional[str] = Field(
        default=None,
        description='Notes UNID - pro zpětnou kompatibilitu',
        examples=['C125868C0046C8EAC1258778007FB80D'],
    )
    clones: Optional[int] = Field(default=None, description='Počet klonovaných položek')
    rlist: Optional[bool] = Field(default=None, description='Identifikace pomocí Registračního listu', examples=[True]
    )
    reference_list: Optional[List[str]] = Field(
        default=None,
        description='Seznam čísel registračních listů',
        examples=['PHA/00951/2020', 'PHA/00953/2020'],
        min_length=0,
    )
    parents: Optional[List[SpecimenParentType]] = Field(
        default=None, description='Rodičovské exempláře', max_length=2000
    )

    def load_dds(self, data):
        self.species = TaxonItemType(
            name_scientific=get_dict_value(data, 'species'),
            name_common_cz=get_dict_value(data, 'common'),
        )
        self.amount = float(get_dict_value_int(data, 'goods_amount'))
        self.quantity = [GoodsQuantityType(
            amount=self.amount,
            units='PCS',
            metric=MetricEnum.NUMBER
        )]
        self.identification = [GoodsIdetificationType(
            identification=get_dict_value(data, 'goods_identification'),
            identifier=get_dict_value(data, 'goods_id'),
        )]
        self.identification_history = None
        self.birth = GoodsBirthType(
            birth_type=BirthTypeEnum.OTHER,
            birth_value=get_dict_value(data, 'goods_birthplace'),
        )
        self.code = get_dict_value(data, 'goods_code')
        self.gender = get_dict_value(data, 'goods_gender')
        self.origin = get_dict_value(data, 'source')
        self.purpose = None
        self.transaction_origin = None
        self.transaction_import = None
        self.transaction_re_export = None
        self.goods_description = get_dict_value(data, 'goods_description')

        self.identifier = str(uuid4())
        self.unid = data['@unid']
        self.pid = data['PID']
        self.clones = get_dict_value_int(data, 'clones')
        self.rlist = get_dict_value(data, 'rlist')
        self.reference_list = get_dict_item_value_list(data, 'goods_reference_list')
        p1 = SpecimenParentType(
            identification=[
                GoodsIdetificationType(
                    identification=get_dict_value(data, 'parent_identification_1'),
                    identifier=get_dict_value(data, 'parent_id_1'),
                )],
            birth=GoodsBirthType(
                birth_type=BirthTypeEnum.OTHER,
                birth_value=get_dict_value(data, 'parent_birth_1'),
            ),
            gender=get_dict_value(data, 'parent_gender_1'),
            origin=get_dict_value(data, 'parent_source_1'),
            transaction_import=TransactionType(
                name='IMPORT',
                permit=get_dict_value(data, 'parent_permit_import_1'),
            ),
            transaction_re_export=TransactionType(
                name='EXPORT',
                permit=get_dict_value(data, 'parent_permit_export_1'),
            ),
            note=get_dict_value(data, 'parent_note_1'),
            reference_list=get_dict_item_value_list(data, 'parent_reference_1'),
            certificate_list=get_dict_item_value_list(data, 'parent_certificate_es_1'),
            acquisition=get_dict_value(data, 'parent_acquisition_1'),
        )
        p2 = SpecimenParentType(
            identification=[
                GoodsIdetificationType(
                    identification=get_dict_value(data, 'parent_identification_2'),
                    identifier=get_dict_value(data, 'parent_id_2'),
                )],
            birth=GoodsBirthType(
                birth_type=BirthTypeEnum.OTHER,
                birth_value=get_dict_value(data, 'parent_birth_2'),
            ),
            gender=get_dict_value(data, 'parent_gender_2'),
            origin=get_dict_value(data, 'parent_source_2'),
            transaction_import=TransactionType(
                name='IMPORT',
                permit=get_dict_value(data, 'parent_permit_import_2'),
            ),
            transaction_re_export=TransactionType(
                name='EXPORT',
                permit=get_dict_value(data, 'parent_permit_export_2'),
            ),
            note=get_dict_value(data, 'parent_note_2'),
            reference_list=get_dict_item_value_list(data, 'parent_reference_2'),
            certificate_list=get_dict_item_value_list(data, 'parent_certificate_es_2'),
            acquisition=get_dict_value(data, 'parent_acquisition_2'),
        )
        self.parents = [p1, p2]
        return self


class DocumentBaseType(BaseModel):
    # Dokument stanoviska
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Metadata stanoviska')
    linked_list: Optional[List[Optional[LinkedType]]] = Field(default=None, description='Seznam provázaných dat')
    comment: Optional[str] = Field(default=None, description='Obecná poznámka')


class DocumentType(DocumentBaseType):
    # Dokument stanoviska
    doc_code: Optional[str] = Field(default=None, description='Kód dokumentu - vazba na šablony', examples=['DD01'])
    metadata: MetadataType = Field(default=None, description='Metadata stanoviska')
    status: Optional[str] = Field(default=None, description='Aktuální stav dokumentu', examples=['PUBLISHED'])
    workflow: Optional[WorkflowListType] = Field(default=None, description='Historie životního cyklu')

# CERT-COMMON ---------------------------------------------

class StatementCertificateCommonsType(BaseModel):
    authority: Optional[PersonExtendedType] = Field(default=None, description='Vydávající autorita')
    holder: Optional[PersonExtendedType] = Field(default=None, description='Držitel')


# CERT-REQ ------------------------------------------------

class StatementCertificateRequestType(StatementCertificateCommonsType):
    # Objekt žádosti o stanovisko k výjimce
    applicant: Optional[PersonExtendedType] = Field(default=None, description='Žadatel')
    from_reg_cert_request: Optional[bool] = Field(default=None, description='Odvozeno z žádosti o RL/CERT')
    intent: Optional[IntentEnum] = Field(default=None, description='Účel výjimky', examples=[IntentEnum.A])
    exception_type: Optional[ExceptionTypeEnum] = Field(
        default=None,
        description='Druh výjimky (na transakci|T, na exemplář|E)',
        examples=[ExceptionTypeEnum.TRANSACTION])
    specimens: Optional[List[SpecimenType]] = Field(default=None, description='Exempláře')


class StatementDocumentCertificateRequestBaseType(DocumentBaseType):
    # Dokument žádosti o stanovisko k výjimce (pro zápis do databáze)
    request: Optional[StatementCertificateRequestType] = Field(default=None, description='Data žádosti o stanovisko')


class StatementDocumentCertificateRequestType(StatementDocumentCertificateRequestBaseType):
    # Žádost o stanovisko k výjimce
    doc_code: Optional[str] = Field(default=None, description='Kód dokumentu - vazba na šablony', examples=['DD01'])
    metadata: MetadataType = Field(default=None, description='Metadata stanoviska')
    status: Optional[str] = Field(default=None, description='Aktuální stav dokumentu', examples=['PUBLISHED'])
    workflow: Optional[WorkflowListType] = Field(default=None, description='Historie životního cyklu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie dokumentu')


# CERT ----------------------------------------------------

class StatementCertificateType(StatementCertificateCommonsType):
    # Stanovisko k výjimce
    recipient: Optional[PersonExtendedType] = Field(default=None, description='Adresát stanoviska')
    specimen: Optional[SpecimenType] = Field(default=None, description='Exemplář')
    id_no: Optional[str] = Field(default=None, description='Číslo jednací stanoviska')
    standalone: Optional[bool] = Field(default=False, description='Samostatné stanovisko')
    approve: Optional[str] = Field(default=None, description='Souhlas')
    standpoint: Optional[str] = Field(default=None, description='Druh stanoviska', examples=['1 - Stanovisko na exemplář podle písmene d)'])
    date_valid: Optional[datetime] = Field(default=None, description='Datum platnosti', examples=['2021-08-30T23:01:14+02:00'])
    subject: Optional[str] = Field(default=None, description='Název stanoviska')
    problem: Optional[str] = Field(default=None, description='Předmět stanoviska')
    reason: Optional[str] = Field(default=None, description='Zdůvodnění')
    parents: Optional[List[SpecimenParentType]] = Field(default=None, description='Rodičovské exempláře')


class StatementCertificateComplementType(BaseModel):
    # Doplněk stanovisko k žádosti (jen to, co není v žádosti)
    recipient: Optional[PersonExtendedType] = Field(default=None, description='Adresát stanoviska')
    species: Optional[TaxonItemType] = Field(default=None, description='Taxon exempláře')
    id_no: Optional[str] = Field(default=None, description='Číslo jednací stanoviska')
    standalone: Optional[bool] = Field(default=False, description='Samostatné stanovisko')
    approve: Optional[str] = Field(default=None, description='Souhlas')
    standpoint: Optional[str] = Field(default=None, description='Druh stanoviska', examples=['1 - Stanovisko na exemplář podle písmene d)'])
    date_valid: Optional[datetime] = Field(default=None, description='Datum platnosti', examples=['2021-08-30T23:01:14+02:00'])
    subject: Optional[str] = Field(default=None, description='Název stanoviska')
    problem: Optional[str] = Field(default=None, description='Předmět stanoviska')
    reason: Optional[str] = Field(default=None, description='Zdůvodnění')


class StatementDocumentCertificateBaseType(DocumentBaseType):
    # Dokument žádosti o stanovisko k výjimce (pro zápis do databáze)
    request: Optional[RelatedType] = Field(default=None, description='Odkaz na žádost o stanovisko')
    statement: Optional[StatementCertificateType] = Field(default=None, description='Data stanoviska')


class StatementDocumentCertificateType(StatementDocumentCertificateBaseType):
    # Dokument stanoviska k výjimce
    doc_code: Optional[str] = Field(default=None, description='Kód dokumentu - vazba na šablony', examples=['DD01'])
    metadata: MetadataType = Field(default=None, description='Metadata stanoviska')
    status: Optional[str] = Field(default=None, description='Aktuální stav dokumentu', examples=['PUBLISHED'])
    workflow: Optional[WorkflowListType] = Field(default=None, description='Historie životního cyklu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie dokumentu')


# PERMIT --------------------------------------------------

class StatementPermitType(BaseModel):
    applicant: Optional[PersonExtendedType] = Field(default=None, description='Žadatel')
    application: Optional[RelatedType] = Field(default=None, description='Žádost o stanovisko')
    general: Optional[bool] = Field(default=None, description='Generální stanovisko')
    agree: Optional[AgreeType] = Field(default=None, description='Vlastní stanovisko')
    reason: Optional[str] = Field(default=None, description='Zdůvodnění stanoviska')
    issuing: Optional[IssuingType] = Field(default=None, description='Informace o vydání')


class StatementDocumentPermitBaseType(DocumentBaseType):
    # Stanovisko k permitu (pro zápis do databáze)
    statement: Optional[StatementPermitType] = Field(default=None, description='Stanovisko k permitu')


class StatementDocumentPermitType(StatementDocumentPermitBaseType):
    # Stanovisko k permitu - CitesDocumentStatementPermitType
    doc_code: Optional[str] = Field(default=None, description='Kód dokumentu - vazba na šablony', examples=['DD01'])
    metadata: MetadataType = Field(default=None, description='Metadata stanoviska')
    status: Optional[str] = Field(default=None, description='Aktuální stav dokumentu', examples=['PUBLISHED'])
    workflow: Optional[WorkflowListType] = Field(default=None, description='Historie životního cyklu')
    history: Optional[list[LogItemType]] = Field(default=None, description='Historie dokumentu')
