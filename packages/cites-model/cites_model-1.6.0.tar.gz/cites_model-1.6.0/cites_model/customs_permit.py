from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from cites_model.cites_common import (
    PermitTypeEnum, GoodsOrderType, RegulationCitesEnum, RegulationEuEnum, DocumentPrincipalCustomsGoodsType,
    DocumentPrincipalCustomsPermitType, PermitSpecialConditionsType, PersonReducedType, GoodsPrincipalType,
    CITES_PURPOSE, MetricEnum)
from pydantic import BaseModel, Field

from cites_model.cites_document import CitesDocumentPrincipalType


class CustomsExchangeCitesPermitType(BaseModel):
    authorized_location: Optional[str] = Field(default=None, description='6. Povolené místo určení živých exemplářů druhů z Přílohy A odebraných z volné přírody\n',)
    comment: Optional[str] = Field(default=None, description='Poznámky')
    conditions: Optional[PermitSpecialConditionsType] = Field(default=None, description='Podmínky vydání permitu')
    consignment_note: Optional[str] = Field(default=None, description='26. Nákladní List/letecký přepravní list číslo')
    country_export: Optional[str] = Field(default=None, description='Země (zpětného) vývozu', examples=['US'])
    country_import: Optional[str] = Field(default=None, description='Země dovozu', examples=['CZ'])
    customs: Optional[DocumentPrincipalCustomsPermitType] = Field(default=None, description='Celní údaje')
    date_issued: Optional[date] = Field(default=None, description='Datum vydání')
    date_valid: Optional[date] = Field(default=None, description='Datum platnosti')
    date_created: Optional[datetime] = Field(default=None, description='Datum vytvoření datové položky')
    date_modified: Optional[datetime] = Field(default=None, description='Datum poslední úpravy datové položky')
    documentation: Optional[str] = Field(default=None, description='24. Doklady k (zpětnému) vývozu ze země (zpětného) vývozu')
    exporter: Optional[PersonReducedType] = Field(default=None, description='Vývozce')
    external: Optional[bool] = Field(default=None, description='Externí permit', examples=[False])
    creator: Optional[str] = Field(default=None, description='Tvůrce datové položky', examples=['CN=Zuzana Karásková/O=ENV'])
    goods: Optional[List[CustomsExchangeCitesGoodsType]] = Field(default=None, description='Položky permitu (zboží)')
    identifier: Optional[str] = Field(default=None, description='Jednoznačný identifikátor datové položky (PID)', examples=['CITDB1FC2L8V'],)
    id_no: Optional[str] = Field(default=None, description='Číslo permitu', examples=['23CZ034504'])
    id_no_internal: Optional[str] = Field(default=None, description='Číslo jednací MŽP')
    id_no_internal_2: Optional[str] = Field(default=None, description='Číslo jednací 2 MŽP')
    importer: Optional[PersonReducedType] = Field(default=None, description='Dovozce')
    issuer: Optional[str] = Field(default=None, description='Vydávající úředník', examples=['Mgr. Zuzana Karásková'])
    issuing_authority: Optional[str] = Field(
        default=None,
        description='Vydávající autorita',
        examples=["Ministerstvo životního prostředí / Ministry of the Environment\nOdbor druhové ochrany a implementace mezinár. závazků\noddělení mezinárodních úmluv\nVršovická 65, 100 10 Praha 10, CZECH REPUBLIC'\n"],
    )
    issuing_signature: Optional[str] = Field(default=None, description='Podpis a úřední razítko', examples=['Ing. Jan Šíma'])
    issuing_officer: Optional[str] = Field(default=None, description='Jméno vydávajícího úředníka', examples=['Mgr. Zuzana Karásková'])
    issuing_place: Optional[str] = Field(default=None, description='Místo vydání', examples=['Praha'])
    permit_type: Optional[PermitTypeEnum] = Field(default=None, description='Typ permitu', examples=[PermitTypeEnum.EXPORT])
    purpose: Optional[str] = Field(default=None, description='Kód účelu - pouze pro EU-CITES', examples=['T'])
    purpose_value: Optional[str] = Field(default=None, description='Textová hodnota účelu - pouze pro EU-CITES', examples=['Komerční účel/Commercial'],)
    token: Optional[str] = Field(default=None, description='Token pro EU-CITES', examples=['CITDB1FC2L8V'])
    stamp: Optional[str] = Field(default=None, description='Číslo bezpečnostní známky', examples=['2098148'])
    used: Optional[str] = Field(default=None, description='indikátor použití permitu (vydán, použit, vrácen, zrušen)', examples=['U'], )
    subject_permitted: Optional[str] = Field(default=None, description='Předmět permitu', examples=['export'])

    def load_production(self, doc: CitesDocumentPrincipalType):
        self.authorized_location = doc.document.location
        self.comment = doc.comment
        self.conditions = doc.permit_conditions
        self.consignment_note = doc.other.consignment_note
        self.country_export = doc.document.country_export
        self.country_import = doc.document.country_import
        self.customs = doc.customs
        self.date_issued = doc.issuing.date_issued.date() if doc.issuing.date_issued else None
        self.date_valid = doc.document.date_valid.date() if doc.document.date_valid else None
        self.date_created = doc.metadata.date_created
        self.date_modified = doc.metadata.date_modified

        self.documentation = doc.other.documentation
        self.exporter = PersonReducedType().load_extended(doc.document.exporter) if doc.document.exporter else None
        self.external = doc.document.permit_is_external
        self.creator = doc.metadata.creator
        self.identifier = doc.metadata.pid
        self.id_no = doc.document.id_no
        self.id_no_internal = doc.document.id_no_local
        self.id_no_internal_2 = doc.document.id_no_list[2] if doc.document.id_no_list and (len(doc.document.id_no_list) > 2) else None
        self.importer = PersonReducedType().load_extended(doc.document.importer) if doc.document.importer else None
        self.issuer = doc.issuing.issuer.name if doc.issuing.issuer else None
        self.issuing_authority = doc.issuing.issuing_authority
        self.issuing_signature = doc.issuing.issuing_signature
        self.issuing_officer = doc.issuing.issuing_official
        self.issuing_place = doc.issuing.issuing_place
        self.permit_type = doc.document.permit_type
        self.purpose = doc.purpose_traces
        self.purpose_value = CITES_PURPOSE[doc.purpose_traces] if doc.purpose_traces in CITES_PURPOSE else None
        self.token = doc.token
        self.stamp = doc.document.stamp_no
        self.used = doc.document.used
        self.subject_permitted = doc.other.subject_permitted
        self.goods = []
        for goods in doc.goods:
            self.goods.append(CustomsExchangeCitesGoodsType().load_production(permit=self, goods=goods))
        return self


class CustomsExchangeCitesGoodsType(BaseModel):
    annex_eu: Optional[RegulationEuEnum] = Field(default=None, description='Příloha EU', examples=[RegulationEuEnum.B])
    appendix_cites: Optional[RegulationCitesEnum] = Field(default=None, description='Příloha CITES', examples=[RegulationCitesEnum.II])
    class_411: Optional[bool] = Field(default=None, description='Zvláštní zacházení podle vyhlášky 411/2008 Sb.', examples=[False],)
    comment: Optional[str] = Field(default=None, description='Poznámka ke zboží')
    common: Optional[str] = Field(default=None, description='Obecný název. Obvykle commonCz/commonEn', examples=['Agapornis Fischerův'])
    common_cz: Optional[str] = Field(default=None, description='Obecný název česky', examples=['Papoušík Fischerův'])
    common_en: Optional[str] = Field(default=None, description='Obecný název anglicky', examples=["Fischer's lovebird"])
    country_last: Optional[str] = Field(default=None, description='Země posledního zpětného vývozu', examples=['US'])
    country_origin: Optional[str] = Field(default=None, description='Země původu', examples=['CZ'])
    customs: Optional[DocumentPrincipalCustomsGoodsType] = Field(default=None, description='Celní údaje zboží')
    date_external: Optional[date] = Field(default=None, description='Datum vydání externího permitu')
    date_last: Optional[date] = Field(default=None, description='Datum vydání permitu země posledního zpětného vývozu')
    date_origin: Optional[date] = Field(default=None, description='Datum vydání permitu země původu')
    date_created: Optional[datetime] = Field(default=None, description='Datum vytvoření datové položky')
    date_modified: Optional[datetime] = Field(default=None, description='Datum poslední úpravy datové položky')
    external: Optional[bool] = Field(default=None, description='Externí permit - permit vydán jinou, než CZ autoritou', examples=[False],)
    creator: Optional[str] = Field(default=None, description='Tvůrce datové položky', examples=['CN=Zbyněk Englic/C=CZ'])
    goods_code: Optional[str] = Field(default=None, description='CITES kód', examples=['LIV'])
    goods_description: Optional[str] = Field(default=None, description='Popis exemplářů (včetně značek, pohlaví, data narození živých zvířat)')
    goods_additional: Optional[str] = Field(default=None, description='Další popis', examples=['odchov/ bred'])
    identifier: Optional[str] = Field(default=None, description='Jednoznačný identifikátor datové položky (PID)', examples=['CIT3ADKD9E1V'],)
    identifier_permit: Optional[str] = Field(default=None, description='Jednoznačný identifikátor datové položky permitu (PID)', examples=['CITDB1FC2L8V'],)
    id_no: Optional[str] = Field(default=None, description='Číslo permitu', examples=['23CZ034504'])
    order: Optional[GoodsOrderType] = Field(default=None, description='Pořadí zboží v permitu')
    origin: Optional[str] = Field(default=None, description='Původ', examples=['C'])
    permit_external: Optional[str] = Field(default=None, description='Číslo externího permitu', examples=['ZW/4514/2011'])
    permit_last: Optional[str] = Field(default=None, description='Číslo permitu země posledního zpětného vývozu', examples=['23US1111111'],)
    permit_origin: Optional[str] = Field(default=None, description='Číslo permitu země původu', examples=['23CZ034504'])
    purpose: Optional[str] = Field(default=None, description='Kód účelu', examples=['T'])
    purpose_value: Optional[str] = Field(default=None, description='Textová hodnota účelu', examples=['Komerční účel/Commercial'])
    quantity: Optional[float] = Field(default=None, description='Množství exemplářů', examples=[100])
    species: Optional[str] = Field(default=None, description='Vědecký název exempláře (latinsky)', examples=['Agapornis fischeri'],)
    units: Optional[str] = Field(default=None, description='Jednotky', examples=['kg'])
    weight: Optional[float] = Field(default=None, description='Hmotnost', examples=[0])

    def load_production(self, permit: CustomsExchangeCitesPermitType, goods: GoodsPrincipalType) -> CustomsExchangeCitesGoodsType:
        self.annex_eu =  RegulationEuEnum(goods.species.regulation_eu) if goods.species.regulation_eu not in [None, ''] else None
        self.appendix_cites =  RegulationCitesEnum(goods.species.regulation_cites) if goods.species.regulation_cites not in [None, ''] else None
        self.class_411 = goods.species.regulation_411
        self.comment = goods.comment
        self.common = goods.field_common
        self.common_cz = goods.field_common_cz
        self.common_en = goods.species.name_common_en
        self.country_last = goods.transaction_re_export.country if goods.transaction_re_export else None
        self.country_origin = goods.transaction_origin.country if goods.transaction_origin else None
        self.customs = goods.goods_customs
        self.date_external = goods.transaction_origin.date_issued.date() if goods.transaction_origin and goods.transaction_origin.date_issued else None
        # self.date_external = goods.transaction_import.date_issued.date() if goods.transaction_import else None
        self.date_last = goods.transaction_re_export.date_issued.date() if goods.transaction_re_export and goods.transaction_re_export.date_issued else None
        self.date_origin = goods.transaction_origin.date_issued.date() if goods.transaction_origin and goods.transaction_origin.date_issued else None
        self.date_created = permit.date_created
        self.date_modified = permit.date_modified
        self.external = permit.external
        self.creator = permit.creator
        self.goods_code = goods.code
        self.goods_description = goods.field_description
        self.goods_additional = goods.goods_additional
        self.identifier = goods.identifier
        self.identifier_permit = permit.identifier
        self.id_no = permit.id_no
        self.order = goods.order
        self.origin = goods.origin
        self.permit_external = goods.transaction_origin.permit if goods.transaction_origin else None
        # self.permit_external = goods.transaction_import.permit  if goods.transaction_import else None
        self.permit_last = goods.transaction_re_export.permit if goods.transaction_re_export else None
        self.permit_origin = goods.transaction_origin.permit if goods.transaction_origin else None
        self.purpose = goods.purpose
        self.purpose_value = CITES_PURPOSE[goods.purpose] if goods.purpose in CITES_PURPOSE else None
        self.quantity = goods.amount
        self.species = goods.species.name_scientific
        self.units = goods.quantity[0].units if goods.quantity else 'PCS'
        self.weight = goods.quantity[0].amount if goods.quantity and goods.quantity[0].metric == MetricEnum.WEIGHT else float(0)
        return self
