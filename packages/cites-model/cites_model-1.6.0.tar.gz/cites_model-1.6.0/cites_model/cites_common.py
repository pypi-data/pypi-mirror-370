from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr
from sysnet_pyutils.data_utils import get_dict_value, get_dict_value_float, get_dict_value_datetime, \
    get_dict_value_bool, get_dict_item_value_list
from sysnet_pyutils.models.general import PersonBaseType, WorkflowType, UserType, MetadataType, BaseEnum, PersonTypeEnum
from sysnet_pyutils.utils import is_valid_uuid, is_valid_pid, is_valid_unid, parse_ldap_name
from typing_extensions import deprecated

from cites_model.cites_swin import SingleWindowType

LOGGER = logging.getLogger(__name__)

class PermitTypeEnum(BaseEnum):
    IMPORT = 'IMPORT'
    EXPORT = 'EXPORT'
    RE_EXPORT = 'RE-EXPORT'
    OTHER = 'OTHER'
    EMPTY = ''
    NULL = None


CITES_PURPOSE = {
    "B": "B - Chov v zajetí nebo umělé pěstování",
    "E": "E - Výchova a vzdělání",
    "G": "G - Botanické zahrady",
    "H": "H - Lovecké trofeje",
    "L": "L - Prosazování právních předpisů",
    "M": "M - Biolékařský výzkum",
    "N": "N - Znovuvysazení nebo vysazení do přírody",
    "P": "P - Osobní účel",
    "Q": "Q - Cirkusy a putovní výstavy",
    "S": "S - Vědecký účel",
    "T": "T - Komerční účel",
    "Z": "Z - Zoologické zahrady",
}

@deprecated('Použijte sysnet_pyutils.models.general.PersonTypeEnum')
class PersonTypeEnumDeprecated(BaseEnum):
    LEGAL_ENTITY = 'legalEntity'
    LEGAL_ENTITY_WO_ICO = 'legalEntityWithoutIco'
    FOREIGN_LEGAL_ENTITY = 'foreignLegalEntity'
    NATURAL_PERSON = 'naturalPerson'
    BUSINESS_NATURAL_PERSON = 'businessNaturalPerson'
    FOREIGN_NATURAL_PERSON = 'foreignNaturalPerson'
    EMPTY = ''
    NULL = None


class CertifiedEnum(BaseEnum):
    CERTIFIED_1 = '1'
    CERTIFIED_2 = '2'
    CERTIFIED_3 = '3'
    CERTIFIED_4 = '4'
    CERTIFIED_5 = '5'
    CERTIFIED_6 = '6'
    CERTIFIED_7 = '7'
    CERTIFIED_8 = '8'
    CERTIFIED_EMPTY = ''


class ValidityEnum(BaseEnum):
    VAL_1 = '1'
    VAL_2 = '2'
    VAL_3 = '3'
    VAL_4 = '4'
    VAL_EMPTY = ''


class IssuingPurposeEnum(BaseEnum):
    PURPOSE_1 = '1'
    PURPOSE_2 = '2'
    PURPOSE_3 = '3'
    PURPOSE_4 = '4'
    PURPOSE_5 = '5'
    PURPOSE_EMPTY = ''


class MetricEnum(BaseEnum):
    WEIGHT = 'weight'
    NUMBER = 'number'
    VOLUME = 'volume'
    OTHER = 'other'


class BirthTypeEnum(BaseEnum):
    DATE = 'DATE'
    INTERVAL = 'INTERVAL'
    MONTH = 'MONTH'
    OTHER = 'OTHER'


class DeliveryEnum(BaseEnum):
    OSOBNE = 'O'
    POSTOU = 'P'


class CertificateTypeEnum(BaseEnum):
    LEG = 'leg'     # LEG - Potvrzení o zákonném získání
    COM = 'com'     # COM - Potvrzení pro obchodní činnosti
    MOV = 'mov'     # MOV - Potvrzení pro přemístění živých exemplářů
    EMPTY = ''


class BaseListType(BaseModel):
    count: Optional[int] = Field(default=0, description='celkový počet vrácených položek', examples=[25])


class BaseEntryListType(BaseListType):
    start: Optional[int] = Field(default=0, description='Počáteční dokument na stránce', examples=[0])
    page_size: Optional[int] = Field(default=10, description='Velikost stránky', examples=[10])
    page: Optional[int] = Field(default=0, description='Požadovaná stránka', examples=[0])
    hits: Optional[int] = Field(default=0, description='celkový počet položek', examples=[25])


class PhoneNumberType(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Název telefonního čísla (mobil, práce, domů)",
        examples=['mobil'],
    )
    prefix: Optional[str] = Field(default=None, description='Národní prefix', examples=[420])
    number: Optional[str] = Field(default=None, description='Vlastní telefonní číslo', examples=['123456789'])


class MailAddressType(BaseModel):
    name: Optional[str] = Field(default=None, description='Název adresa elektronické pošty (práce, domů)',examples=['domů'])
    email: Optional[EmailStr] = Field(default=None, description='Adresa elektronické pošty', examples=['josef.svejk@example.com'])


class PersonReducedType(BaseModel):
    address: Optional[List[str]] = Field(
        default=None,
        description='Řádky adresy',
        examples=['Lipovec 39', '538 43 Třemošnice', 'CZ'],
    )
    country: Optional[str] = Field(default=None, description='Kód země', examples=['CZ'])
    description_person: Optional[str] = Field(
        default=None,
        description='Popis osoby',
        examples=['ENGLIC, Zbyněk\nLipovec 39\n538 43 Třemošnice\nCZ\n'],
    )
    identifier: Optional[str] = Field(default=None, description='Jednoznačný identifikátor osoby', examples=['ZKAA7K6D4KI2'])
    name: Optional[str] = Field(default=None, description='Název osoby', examples=['ENGLIC, Zbyněk'])

    def load_extended(self, person: PersonExtendedType):
        self.address = person.address.split('\n') if person.address else None
        self.country = person.country.code
        self.description_person = person.person_printable
        self.identifier = person.identifier
        self.name = person.name
        return self

class PersonExtendedType(PersonBaseType):
    identifier: Optional[str] = Field(default=None, description='Hlavní identifikátor osoby')
    person_type: Optional[PersonTypeEnum] = Field(
        default=None,
        description='Typ osoby (zdroj CRŽP): \n- legalEntity: tuzemská právnická osoba\n- legalEntityWithoutIco: tuzemská právnická osoba bez IČO\n- foreignLegalEntity: zahraniční právnická osoba\n- businessNaturalPerson: tuzemská fyzická osoba podnikající\n- naturalPerson: tuzemská fyzická osoba nepodnikající\n- foreignNaturalPerson: zahraniční fyzická osoba podnikající\n',
        examples=['legalEntity'],
    )
    person_printable: Optional[str] = Field(default=None, description='Název osoby pro tisk', examples=['B.A.R. Reptofilia'])
    birthdate: Optional[datetime] = Field(default=None, examples=['2021-08-30T23:01:14.274085491+15:55'])
    credential: Optional[str] = Field(default=None, description='Číslo průkazu totožnosti')
    credential_type: Optional[str] = Field(default=None, description='Typ průkazu totožnosti')
    phone: Optional[List[Optional[PhoneNumberType]]] = Field(default=None, description='Telefonní číslo')
    email: Optional[List[Optional[MailAddressType]]] = Field(default=None, description='Elektronická pošta')
    special_flags: Optional[List[Optional[str]]] = Field(
        default=None,
        description='Speciální textové značení',
        examples=['importer_special=0', 'importer_transit=0'],
    )

    def parse_identifier(self):
        if self.identifier in [None, '']:
            return
        if is_valid_uuid(str(self.identifier)):
            self.uuid = str(UUID(str(self.identifier)))
        elif is_valid_pid(str(self.identifier)):
            self.pid = str(str(self.identifier))
        elif is_valid_unid(str(self.identifier)):
            self.unid = str(str(self.identifier))


class PersonHistoryItemType(PersonBaseType):
    date_from: Optional[datetime] = Field(default=None, description='Počáteční datum vlastnictví', examples=['2021-08-30T23:01:14.274085491+15:55'])
    date_to: Optional[datetime] = Field(default=None, description='Konečné datum vlastnictví', examples=['2021-08-30T23:01:14.274085491+15:55'])


class GeneralType(BaseModel):
    id_no: Optional[str] = Field(default=None, description='Číslo dokumentu', examples=['23CZ123456'])
    id_no_local: Optional[str] = Field(default=None, description='Lokální číslo dokumentu', examples=['23CZ123456'])
    id_no_list: Optional[List[Optional[str]]] = Field(default=None, description='Seznam všech čísel dokumentu', examples=['23CZ123456'])
    authorized: Optional[bool] = Field(default=False, description='Indikuje, zda je dokument autorizován a připraven pro publikaci')
    permit_type: Optional[PermitTypeEnum] = Field(default=None, description='typ permitu')
    permit_type_other: Optional[str] = Field(default=None, description='popis typu permitu, když OTHER')
    permit_is_external: Optional[bool] = Field(default=False, description='Externí permit')
    permit_token: Optional[str] = Field(default=None, description='Token externího permitu')
    location: Optional[str] = Field(default=None, description='Povolené místo určení živých exemplářů druhů z přílohy A odebraných z volné přílohy\n')
    applicant: Optional[PersonExtendedType] = Field(default=None, description='Žadatel')
    applicant_agent: Optional[PersonExtendedType] = Field(default=None, description='Zástupce žadatele')
    exporter: Optional[PersonExtendedType] = Field(default=None, description='Vývozce')
    importer: Optional[PersonExtendedType] = Field(default=None, description='Dovozce')
    holder: Optional[PersonExtendedType] = Field(default=None, description='Držitel')
    holder_history: Optional[List[Optional[PersonHistoryItemType]]] = Field(default=None, description='Historie vlastníků nebo držitelů')
    country_export: Optional[str] = Field(default=None, description='Země (zpětného) vývozu', examples=['CZ'])
    country_import: Optional[str] = Field(default=None, description='Země dovozu', examples=['US'])
    stamp_no: Optional[str] = Field(default=None, description='Bezpečnostní známka č.')
    date_acquired: Optional[datetime] = Field(default=None, description='Datum získání', examples=['2021-08-30T23:01:14.274085491+15:55'])
    date_delivered: Optional[datetime] = Field(default=None, description='Datum přijetí', examples=['2021-08-30T23:01:14.274085491+15:55'])
    date_valid: Optional[datetime] = Field(default=None, description='Poslední den platnosti', examples=['2021-08-30T23:01:14.274085491+15:55'])
    exhibition_no: Optional[str] = Field(default=None, description='Evidenční číslo výstavy')
    status: Optional[str] = Field(default=None, description='Aktuální stav dokumentu', examples=['AUTHORIZED'])
    used: Optional[str] = Field(default=None, description='Aktuální stav použití dokumentu', examples=['I'])


class TransactionType(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description='Název transakce (IMPORT, EXPORT, RE-EXPORT, OTHER, ...)',
        examples=['IMPORT'],
    )
    permit: Optional[str] = Field(default=None, description='Číslo dokumentu', examples=['23US123456'])
    date_issued: Optional[datetime] = Field(default=None, description='datum vydání dokumentu', examples=['2021-08-30T23:01:14.274085491+15:55'])
    date_realized: Optional[datetime] = Field(default=None, description='datum provedení transakce', examples=['2021-08-30T23:01:14.274085491+15:55'])
    date_canceled: Optional[datetime] = Field(default=None, description='datum zrušení transakce', examples=['2021-08-30T23:01:14.274085491+15:55'])
    country: Optional[str] = Field(default=None, description='Země transakce', examples=['US'])


class ConditionsType(BaseModel):
    certified: Optional[List[Optional[CertifiedEnum]]] = Field(
        default=None,
        description='Tímto se potvrzuje, že uvedené exempláře (podmínka 1 až 8)',
        examples=['2', '5', '7'])
    validity: Optional[List[Optional[ValidityEnum]]] = Field(
        default=None,
        description='Zvláštní podmínky platnosti dokladu',
        examples=['1', '3'])
    valid_for_holder: Optional[bool] = Field(default=None, description='Platí pouze pro držitele', examples=[True])
    conditions: Optional[str] = Field(
        default=None,
        description='Zvláštní podmínky (permit)',
        examples=['Návrat z dočasného vývozu./ Return from temporary stay abroad.'],
    )
    issuing_purpose: Optional[List[Optional[IssuingPurposeEnum]]] = Field(
        default=None,
        description='Tento doklad je vydáván za účelem',
        examples=['1', '3', '4'])


class IssuingType(BaseModel):
    issuing_authority_identifier: Optional[str] = Field(default=None, description='Identifikátorr vydávající autorita', examples=['env'])
    issuing_authority: Optional[str] = Field(default=None, description='Vydávající autorita', examples=['MŽP'])
    issuing_signature: Optional[str] = Field(default=None, description='Oprávněná úřední osoba', examples=['Mgr. Jiří Novák, MBA'])
    issuing_official: Optional[str] = Field(default=None, description='Jméno vydávajícího úředníka', examples=['Mgr. Jiří Novák, MBA'])
    issuing_place: Optional[str] = Field(default=None, description='Místo vydání', examples=['Praha'])
    date_issued: Optional[datetime] = Field(default=None, description='Datum vydání (IssuingDate)', examples=['2021-08-30T23:01:14.274085491+15:55'])
    issuer: Optional[PersonBaseType] = Field(default=None, description='Vydavatel')


class OtherType(BaseModel):
    certificate_type: Optional[CertificateTypeEnum] = Field(
        default=None,
        description='Typ potvrzení podle číselníku:\n  * LEG - Potvrzení o zákonném získání\n  * COM - Potvrzení pro obchodní činnosti\n  * MOV - Potvrzení pro přemístění živých exemplářů\n',
    )
    certificate_form_version: Optional[str] = Field(default=None, description='Verze formuláře potvrzení (aktuálně 2)')
    customs: Optional[str] = Field(default=None, description='Celní údaje')
    documentation: Optional[str] = Field(default=None, description=' Doklady k (zpětnému) vývozu ze země (zpětného) vývozu')
    documents_to_authority: Optional[bool] = Field(default=None, description='Doklady byly předány vydávajícímu orgánu')
    documents_to_customs: Optional[bool] = Field(default=None, description='Doklady byly předány celnímu orgánu')
    consignment_note: Optional[str] = Field(default=None, description='Nákladní/pořepravní list')
    subject_permitted: Optional[str] = Field(default=None, description='Předmět povolení')
    # od verze 1.5
    annex: Optional[List[Optional[str]]] = Field(default=None, description='Seznam příloh žádosti (attachment)')
    comment_registration: Optional[str] = Field(default=None, description='Poznámka k Registračnímu listu (commentReg)')
    comment_certificate: Optional[str] = Field(default=None, description='Poznámka k Výjimce (commentCert)')
    parent_info: Optional[str] = Field(default=None, description='Údaje o rodičovských exemplářích')


class PermitSpecialConditionsType(BaseModel):
    annex_pages: Optional[int] = Field(default=None, description='Počet stran příloh', examples=[6])
    permit_canceled: Optional[str] = Field(default=None, description='Vydáno namísto zrušeného povolení (permit)', examples=['23CZ000022'])
    max_length: Optional[str] = Field(default=None, description='Maximální délka exempláře v cm', examples=['32'])
    photo_pages: Optional[int] = Field(default=None, description='Počet stran fotografií exemplářů', examples=[0])
    plastron: Optional[str] = Field(default=None, description='Délka plastronu v cm', examples=['4.6'])
    karapax: Optional[str] = Field(default=None, description='Délka karapaxu v cm', examples=['3.4'])
    other: Optional[List[Optional[str]]] = Field(default=None, description='Další podmínky', examples=['Podmínka 1', 'Podmínka 2'])
    text: Optional[List[Optional[str]]] = Field(default=None, description='Položky s volným textem podmínek')
    transaction: Optional[List[Optional[str]]] = Field(
        default=None,
        description='Souhrn transakčních podmínek',
        examples=[
            'bezpečnostní známka č./ security stamp No. 2098148',
            'příloha/ annex: =6= stran/ pages'])


class DocumentPrincipalCustomsPermitType(BaseModel):
    certificate: Optional[str] = Field(default=None, description='Číslo celního dokladu', examples=['23CZ6100002BJNUMP0'])
    comment: Optional[str] = Field(default=None, description='Poznámka k celním údajům')
    date_customs: Optional[datetime] = Field(
        default=None,
        description='Datum použití permitu',
        examples=['2021-08-30T23:01:14.274085491+15:55'],
    )
    date_returned: Optional[datetime] = Field(
        default=None,
        description='Datum vrácení nepoužitého permitu',
        examples=['2021-08-30T23:01:14.274085491+15:55'],
    )
    type_customs: Optional[str] = Field(default=None, description='Typ celního dokladu', examples=['SWIN'])


class TaxonItemType(BaseModel):
    pid: Optional[str] = Field(default=None, description='PID taxonu', examples=['MBOA7HNBDJTR'])
    uuid: Optional[str] = Field(default=None, description='identifikátor položky zboží', examples=['9d6e2fc9-ca1f-4504-a54b-c8263a21c678'])
    id_species_plus: Optional[List[Optional[str]]] = Field(default=None, description='Identifikátor species+')
    name_scientific: Optional[str] = Field(default=None, description='Vědecký název', examples=['Atelopus zeteki'])
    name_common_cz: Optional[str] = Field(default=None, description='Obecný název (česky))', examples=['atelopus panamský'])
    name_common_en: Optional[str] = Field(default=None, description='Obecný název (anglicky)', examples=['Golden Arrow Poison Frog'])
    regulation_cites: Optional[str] = Field(default=None, description='Příloha CITES', examples=['I'])
    regulation_eu: Optional[str] = Field(default=None, description='Příloha EU', examples=['A'])
    regulation_411: Optional[bool] = Field(default=None, description='Zvláštní ochrana', examples=[False])
    error: Optional[bool] = Field(default=False, description='Taxon error')


class GoodsQuantityType(BaseModel):
    metric: Optional[MetricEnum] = Field(default=MetricEnum.NUMBER, description='Metrika (hmotnost, počet, objem, jiná)')
    amount: Optional[float] = Field(default=float(1), description='Množství')
    units: Optional[str] = Field(default=None, description='Jednotky', examples=['PCS'])


class GoodsIdetificationType(BaseModel):
    identification: Optional[str] = Field(
        default=None,
        description='Identifikace exemplářů (čip, kroužek, fotografie, jiné)',
        examples=['C'])
    identifier: Optional[str] = Field(default=None, description='číslo identifikačníchh prostředků', examples=['941000025010989'])


class GoodsIdetificationHistoryItemType(GoodsIdetificationType):
    date_valid_from: Optional[datetime] = Field(default=None, examples=['2021-08-30T23:01:14.274085491+15:55'])
    date_valid_to: Optional[datetime] = Field(default=None, examples=['2021-08-30T23:01:14.274085491+15:55'])


class GoodsBirthType(BaseModel):
    birth_place: Optional[str] = Field(default=None, description='místo narození', examples=['LIV'])
    birth_type: Optional[BirthTypeEnum] = Field(default=None, description='Typ určení data narození')
    birth_value: Optional[str] = Field(default=None, description='Hodnota data narození, není-li DATE')
    birth_date: Optional[datetime] = Field(default=None, description='Datum narození', examples=['2021-08-30T23:01:14.274085491+15:55'])


class GoodsItemBaseType(BaseModel):
    species: Optional[TaxonItemType] = Field(default=None, description='Název zboží')
    amount: Optional[float] = Field(default=float(1), description='Množství')
    quantity: Optional[List[Optional[GoodsQuantityType]]] = Field(default=None, description='Strukturované množství')
    identification: Optional[List[Optional[GoodsIdetificationType]]] = Field(default=None, description='Identifikace exemplářů')
    identification_history: Optional[List[Optional[GoodsIdetificationHistoryItemType]]] = Field(default=None, description='Historie identifikací')
    birth: Optional[GoodsBirthType] = Field(default=None, description='Údaje o narození exempláře')
    code: Optional[str] = Field(default=None, description='Kód exempláře', examples=['LIV'])
    gender: Optional[str] = Field(default=None, description='Pohlaví exempláře', examples=['JUV'])
    origin: Optional[str] = Field(default=None, description='Původ', examples=['T'])
    purpose: Optional[str] = Field(default=None, description='Účel', examples=['T'])
    transaction_origin: Optional[TransactionType] = Field(default=None, description='Transakce původ')
    transaction_import: Optional[TransactionType] = Field(default=None, description='Transakce dovoz')
    transaction_re_export: Optional[TransactionType] = Field(default=None, description='Transakce re-export')
    goods_description: Optional[str] = Field(default=None, description='Popis exempláře - pole Notes: description')


class GoodsOrderType(BaseModel):
    text_value: Optional[str] = Field(default=None, description='pořadí zboží v permitu', examples=['A'])
    num_value: Optional[int] = Field(default=None, description='pořadové číslo zboží v permitu', examples=[1])


class GoodsRequestType(BaseModel):
    annex: Optional[str] = Field(default=None, description='Příloha žádosti (attachment)')
    comment_registration: Optional[str] = Field(default=None, description='Poznámka k Registračnímu listu (commentReg)')
    comment_certificate: Optional[str] = Field(default=None, description='Poznámka k Výjimce (commentCert)')
    parent_info: Optional[str] = Field(default=None, description='Údaje o rodičovských exemplářích')
    date_import: Optional[datetime] = Field(default=None, description='Datum dovozu exempláře (goods_importdate)')


class DocumentPrincipalCustomsGoodsType(BaseModel):
    certificate: Optional[str] = Field(default=None, description='Číslo celního dokladu', examples=['23CZ6100002BJNUMP0'])
    comment: Optional[str] = Field(default=None, description='Poznámka k celním údajům')
    date_customs: Optional[datetime] = Field(default=None, description='Datum použití permitu', examples=['2021-08-30T23:01:14.274085491+15:55'])
    dead: Optional[float] = Field(default=None, description='Počet uhynulých exemplářů')
    id_customs: Optional[str] = Field(default=None, description='Celní identifikátor')
    quantity: Optional[float] = Field(default=None, description='Proclené množství')
    type_customs: Optional[str] = Field(default=None, description='Typ celního dokladu', examples=['SWIN'])


class RelatedType(BaseModel):
    title: Optional[str] = Field(default=None, description='Název souvisejícího dokumentu')
    unid: Optional[str] = Field(default=None, description='Domino universal ID', examples=['3005277CB984B7FFC12587890060E2BF'])
    pid: Optional[str] = Field(default=None, description='Unique identifier', examples=['MBOA7HNBDJTR'])
    uuid: Optional[str] = Field(default=None, description='Unique identifier')
    id_no: Optional[str] = Field(default=None, description='Číslo dokumentu', examples=['23CZ123456'])
    form: Optional[str] = Field(default=None, description='Formulář', examples=['certificate'])


class GoodsPrincipalTypeWrite(GoodsItemBaseType):
    identifier: Optional[str] = Field(default=None, description='identifikátor položky zboží', examples=['24CZ123456*1'])
    unid: Optional[str] = Field(default=None, description='Notes UNID - pro zpětnou kompatibilitu', examples=['C125868C0046C8EAC1258778007FB80D'])
    pid: Optional[str] = Field(default=None, description='Dvanaáctimístný identifikátor - pro zpětnou kompatibilitu', examples=['CIT123456789'])
    order: Optional[GoodsOrderType] = Field(default=None, description='Pořadí zboží v permitu')
    goods_customs: Optional[DocumentPrincipalCustomsGoodsType] = Field(default=None, description='Celní údaje zboží')
    goods_additional: Optional[str] = Field(default=None, description='Další popis exempláře - pole Notes goods_additional')
    goods_description_base: Optional[str] = Field(default=None, description='Základní popis exempláře - pole Notes: goods_description')
    net_mass: Optional[float] = Field(default=None, description='Čistá hmotnost exempláře/ů', examples=[8.54])
    units: Optional[str] = Field(default=None, description='Jednotky', examples=['PCS'])
    amount_printable: Optional[str] = Field(default=None, description='Tištitelná podoba množství', examples=['=== 12 ks/pcs ==='])
    goods_cloning: Optional[str] = Field(default=None, description='Klonování exempláře')
    requested_document: Optional[str] = Field(default=None, description='Požadovaný dokument')
    requested_statement: Optional[str] = Field(default=None, description='Požadované stanovisko')
    authority_decision_id: Optional[str] = Field(default=None, description='Rozhodnutí úřadu')
    statement_type: Optional[str] = Field(default=None, description='Typ stanoviska vědeckého orgánu AOPK/Generální [A/G] (env_resolution)', examples=['G'])
    statement_issued: Optional[bool] =  Field(default=None, description='Stanovisko vydáno (is_statement)')
    single_window: Optional[SingleWindowType] = Field(default=None, description='Údaje získané ze SWIN')
    used: Optional[str] = Field(default=None, description='Aktuální stav použití položky dokumentu', examples=['I'])
    comment: Optional[str] = Field(default=None, description='Komentář ke zboží')
    related: Optional[List[Optional[RelatedType]]] = Field(default=None, description='Související dokumenty')


class GoodsPrincipalType(GoodsPrincipalTypeWrite):
    history: Optional[List[Optional[str]]] = Field(default=None, description='Historie dokumentu ($History)')

    def load_dds(self, goods_item):
        log = logging.getLogger(__name__)
        log.info(f"{__name__}.load_dds: {type(goods_item)}")

        try:
            quantity = get_dict_value_float(goods_item, 'quantity')
            q_units = get_dict_value(goods_item, 'quantity_unit')
            net_mass: Union[float, None] = get_dict_value_float(goods_item, 'net_mass')
            nm_units = get_dict_value(goods_item, 'mass')
            amount = quantity
            units = q_units
            if net_mass > float(0):
                amount = net_mass
                units = nm_units
            swin_transaction = get_dict_value(goods_item, 'transaction')
            if swin_transaction not in [None, '']:
                lines = swin_transaction.split('\n')
                swin_transaction = [line for line in lines if line.strip()]
            swin_identifier = get_dict_value(goods_item, 'identifier_customs')
            swin_identifier_list = None
            if swin_identifier not in [None, '']:
                lines = swin_identifier.split('\n')
                swin_identifier_list = [line for line in lines if line.strip()]
            swin_change = []
            for i in range(200):
                item_name = f"swin_change_{i + 1}"
                v = get_dict_value(goods_item, item_name)
                if v is not None:
                    swin_change.append(v)
                else:
                    break
            if not bool(swin_change):
                swin_change = None
            self.species = TaxonItemType(
                pid=None,
                name_scientific=get_dict_value(goods_item, 'species'),
                name_common_cz=get_dict_value(goods_item, 'common'),
                name_common_en=get_dict_value(goods_item, 'common_en'),
                regulation_cites=get_dict_value(goods_item, 'appendix_cites'),
                regulation_eu=get_dict_value(goods_item, 'annex_ec'),
                regulation_411=False,
                error=get_dict_value_bool(goods_item, 'taxonError')
            )
            log.info(f"{__name__}.load_dds SPECIES")
            self.amount = amount
            self.quantity = [
                GoodsQuantityType(
                    metric=MetricEnum.NUMBER,
                    units=q_units,
                    amount=quantity
                ),
                GoodsQuantityType(
                    metric=MetricEnum.WEIGHT,
                    units=nm_units,
                    amount=net_mass
                )
            ]
            log.info(f"{__name__}.load_dds QUANTITY")
            self.identification = []
            self.identification_history = []
            self.birth = GoodsBirthType()
            self.code = get_dict_value(goods_item, 'goods_code')
            self.gender = None
            self.origin = get_dict_value(goods_item, 'origin')
            if self.origin in [None, '']:
                self.origin = get_dict_value(goods_item, 'source')
            self.purpose = get_dict_value(goods_item, 'purpose')
            self.transaction_origin = TransactionType(
                name='ORIGIN',
                country=get_dict_value(goods_item, 'origin_country'),
                permit=get_dict_value(goods_item, 'origin_permit'),
                date_issued=get_dict_value_datetime(goods_item, 'origin_permit_issued'),
                date_realized=None,
                date_canceled=None)
            log.info(f"{__name__}.load_dds TRANSACTION_ORIGIN")

            self.transaction_import = TransactionType()
            self.transaction_re_export = TransactionType(
                name='LAST_RE_EXPORT',
                country=get_dict_value(goods_item, 'last_reexport_country'),
                permit=get_dict_value(goods_item, 'last_reexport_permit'),
                date_issued=get_dict_value_datetime(goods_item, 'last_reexport_permit_issued'),
                date_realized=None,
                date_canceled=None)
            log.info(f"{__name__}.load_dds TRANSACTION_RE_EXPORT")
            self.goods_description = get_dict_value(goods_item, 'description')
            goods_additional = get_dict_value(goods_item, 'goods_additional')
            if goods_additional is not None and isinstance(goods_additional, list):
                goods_additional = "\n".join(goods_additional)
            self.goods_additional = goods_additional
            self.goods_description_base = get_dict_value(goods_item, 'goods_description')
            self.identifier = f"{get_dict_value(goods_item, 'PID')}*{get_dict_value(goods_item, 'order')}"
            self.unid = get_dict_value(goods_item, '@unid')
            self.pid = get_dict_value(goods_item, 'PID')
            self.order = GoodsOrderType(
                text_value=get_dict_value(goods_item, 'orderString'),
                num_value=get_dict_value(goods_item, 'order'))
            log.info(f"{__name__}.load_dds ORDER")

            self.goods_customs = DocumentPrincipalCustomsGoodsType(
                certificate=get_dict_value(goods_item, 'certificate_customs'),
                comment=None,
                date_customs=get_dict_value_datetime(goods_item, 'date_customs'),
                dead=get_dict_value_float(goods_item, 'dead_customs'),
                id_customs=swin_identifier,
                quantity=get_dict_value_float(goods_item, 'quantity_customs'),
                type_customs=get_dict_value(goods_item, 'type_customs'),
            )
            log.info(f"{__name__}.load_dds GOODS_CUSTOMS")
            self.net_mass = net_mass
            self.units = get_dict_value(goods_item, 'mass')
            self.amount_printable = f"={amount}= {units}"
            self.goods_cloning = None
            self.requested_document = None
            self.requested_statement = None
            self.authority_decision_id = None
            self.statement_type = get_dict_value(goods_item, 'env_resolution')
            self.single_window = SingleWindowType(
                version=get_dict_value(goods_item, 'swin'),
                transaction_list=swin_transaction,
                identifier_list=swin_identifier_list,
                change_json_list=swin_change,
                note=None
            )
            self.used = get_dict_value(goods_item, 'used')
            self.comment = get_dict_value(goods_item, 'comment')
            self.related = []
            self.history = get_dict_item_value_list(goods_item, '$History')
            log.info(f"{__name__}.load_dds DONE")
            return self
        except Exception as e:
            LOGGER.error(f"{__name__}.GoodsPrincipalType.load_dds: {str(e)}")
            return None

    @property
    def field_common(self) -> Optional[str]:
        common = ''
        common_cz = self.species.name_common_cz
        common_en = self.species.name_common_en
        if common_cz not in [None, ''] and common_en not in [None, '']:
            common = f"{common_cz}/ {common_en}"
        elif common_cz in [None, ''] and common_en not in [None, '']:
            common = common_en
        elif common_cz not in [None, ''] and common_en in [None, '']:
            common = common_cz
        return common

    @property
    def field_common_cz(self) -> Optional[str]:
        out = ''
        if self.species.name_common_cz in [None, '']:
            return out
        out = self.species.name_common_cz
        return out

    @property
    def field_description(self) -> Optional[str]:
        dl = []
        if self.code not in [None, '']:
            dl.append(self.code)
        if self.goods_description not in [None, '']:
            dl.append(self.goods_description)
        if self.goods_additional not in [None, '']:
            dl.append(self.goods_additional)
        out = '\n'.join(dl)
        return out


class WorkflowCitesType(WorkflowType):

    def load_data(self, node_code, node_name, responsible, date_execution, executor, status_from, status_to):
        self.node_code = node_code
        self.node_name = node_name
        self.responsible = responsible
        self.date_execution = date_execution
        self.executor = executor
        self.status_from = status_from
        self.status_to = status_to



class WorkflowListType(BaseListType):
    status: Optional[str] = Field(default=None, description='Aktuální status dokumentu')
    entries: Optional[List[Optional[WorkflowCitesType]]] = Field(default=None, description='seznam uzlů životního cyklu')

    def load_dds(self, data):
        self.entries = []
        form = data['@form']
        rejected = get_dict_value_bool(data, 'rejected')
        id_no = get_dict_value(data, 'id_no')
        id_local = get_dict_value(data, 'ID_NO_Local')
        # authorized = get_dict_value_bool(data, 'Authorized')
        # statement = get_dict_value(data, 'statement')           # TODO statement
        # processing = get_dict_value(data, 'processing')
        s1_date_created = get_dict_value_datetime(data, '@created')
        s1_creator = get_dict_value(data, 'From')
        s2_date_authorized = get_dict_value_datetime(data, 'Date_Authorized')
        if s2_date_authorized is None:
            s2_date_authorized = get_dict_value_datetime(data, 'date_authorized')
        s2_authorized_by = get_dict_value(data, 'AuthorizedBy')
        s3_date_delivered = get_dict_value_datetime(data, 'Date_Delivered')
        if s3_date_delivered is None:
            s3_date_delivered = get_dict_value_datetime(data, 'DeliveredDate')
        s3_delivered_by = get_dict_value(data, 'User_Delivered')
        s4_date_processing = get_dict_value_datetime(data, 'Date_Processing')
        s4_processing_by = get_dict_value(data, 'User_Processing')
        s5_date_statement_request = get_dict_value_datetime(data, 'Date_StatementType')
        s5_statement_request_by = get_dict_value(data, 'StatementRequestBy')
        s6_date_processed = get_dict_value_datetime(data, 'Date_Processed')
        s6_processed_by = get_dict_value(data, 'User_Processed')
        s7_date_approved = get_dict_value_datetime(data, 'date_approved')
        s7_approved_by = get_dict_value(data, 'ApprovedBy')
        s8_date_in_process = get_dict_value_datetime(data, 'Date_inProcess')
        s8_date_in_process_opr = get_dict_value_datetime(data, 'Date_inProcess_opr')
        if isinstance(s8_date_in_process_opr, datetime):
            s8_date_in_process = s8_date_in_process_opr
        s8_in_process_by = get_dict_value(data, 'inProcessBy')
        s9_date_statement_issued = get_dict_value_datetime(data, 'Date_statementsIssued')
        s9_statement_issued_by = get_dict_value(data, 'statementsIssuedBy')
        s99_date_rejected = get_dict_value_datetime(data, 'Date_Rejected')
        s99_rejected_by = get_dict_value(data, 'User_Processed')
        s10_date_application = get_dict_value_datetime(data, 'Date_Application')
        s10_applicant = get_dict_value(data, 'holder_fullname')
        s11_date_accepted = get_dict_value_datetime(data, 'Date_Accepted')
        s11_accepted_by = None
        s12_date_processing = get_dict_value_datetime(data, 'Date_Processing')
        s12_processing_by = get_dict_value(data, 'User_Processing')
        status = None
        if s1_date_created is not None:
            cn, ldap_name = parse_ldap_name(s1_creator)
            w1 = WorkflowCitesType()
            w1.node_code = '1-created'
            w1.node_name = 'vytvořeno'
            w1.responsible = None
            w1.date_execution = s1_date_created
            w1.executor = UserType(dn=ldap_name, name=cn)
            w1.status_from = None
            w1.status_to = '2-authorized'
            status = w1.node_code
            self.entries.append(w1)
        if (form == 'statement') and ('permit_type' in data):       # stanovisko k permitu
            status_read = get_dict_value(data, 'status')
            if s2_date_authorized is not None:
                cn, ldap_name = parse_ldap_name(s2_authorized_by)
                w2 = WorkflowCitesType()
                w2.node_code = '2-authorized'
                w2.node_name = 'autorizováno'
                w2.responsible = None
                w2.date_execution = s2_date_authorized
                w2.executor = UserType(dn=ldap_name, name=cn)
                w2.status_from = '1-created'
                w2.status_to = '3-approved'
                status = w2.node_code
                self.entries.append(w2)
            if s7_date_approved is not None:
                cn, ldap_name = parse_ldap_name(s7_approved_by)
                w7 = WorkflowCitesType()
                w7.node_code = '3-approved'
                w7.node_name = 'schváleno'
                w7.responsible = None
                w7.date_execution = s7_date_approved
                w7.executor = UserType(dn=ldap_name, name=cn)
                w7.status_from = '2-authorized'
                w7.status_to = None
                status = w7.node_code
                self.entries.append(w7)
            if status_read in [None, '']:       # Stará schválená stanoviska
                cn, ldap_name = parse_ldap_name(s1_creator)
                w7 = WorkflowCitesType()
                w7.node_code = '3-approved'
                w7.node_name = 'schváleno'
                w7.responsible = None
                w7.date_execution = get_dict_value_datetime(data, 'Date_Modified')
                w7.executor = UserType(dn=ldap_name, name=cn)
                w7.status_from = '2-authorized'
                w7.status_to = None
                status = w7.node_code
                self.entries.append(w7)
                pass
        else:
            if s2_date_authorized is not None:
                cn, ldap_name = parse_ldap_name(s2_authorized_by)
                w2 = WorkflowCitesType()
                w2.node_code = '2-authorized'
                w2.node_name = 'autorizováno'
                w2.responsible = None
                # w2.date_execution=s2_date_authorized.strftime('%Y-%m-%dT%H:%M:%SZ')
                w2.date_execution = s2_date_authorized
                w2.executor = UserType(dn=ldap_name, name=cn)
                w2.status_from = '1-created'
                w2.status_to = '3-delivered'
                status = w2.node_code
                self.entries.append(w2)
            if form == 'regcertrequest':        # žádost o RL nebo výjimku
                if s3_date_delivered is not None:
                    cn, ldap_name = parse_ldap_name(s3_delivered_by)
                    w3 = WorkflowCitesType()
                    w3.node_code = '3-delivered'
                    w3.node_name = f'žádost doručena podatelnou pod čj. {id_no}'
                    w3.responsible = None
                    w3.date_execution = s3_date_delivered
                    w3.executor = UserType(dn=ldap_name, name=cn)
                    w3.status_from = '2-authorized'
                    w3.status_to = '10-application'
                    status = w3.node_code
                    self.entries.append(w3)
                if s10_date_application is not None:
                    cn, ldap_name = parse_ldap_name(s10_applicant)
                    w10 = WorkflowCitesType()
                    w10.node_code = '10-application'
                    w10.node_name = 'žádost přijata k vyřízení'
                    w10.responsible = None
                    w10.date_execution = s10_date_application
                    w10.executor = UserType(dn=ldap_name, name=cn)
                    w10.status_from = '3-delivered'
                    w10.status_to = '11-acceptation'
                    status = w10.node_code
                    self.entries.append(w10)
                if s11_date_accepted is not None:
                    cn = ldap_name = None
                    if s11_accepted_by not in [None, ''] and isinstance(s11_accepted_by, str):
                        cn, ldap_name = parse_ldap_name(s11_accepted_by)
                    w11 = WorkflowCitesType()
                    w11.node_code = '11-accepted'
                    w11.node_name = 'žádost akceptována'
                    w11.responsible = None
                    w11.date_execution = s11_date_accepted
                    w11.executor = UserType(dn=ldap_name, name=cn)
                    w11.status_from = '10-delivered'
                    w11.status_to = '12-processed'
                    status = w11.node_code
                    self.entries.append(w11)
                if s12_date_processing is not None:
                    cn, ldap_name = parse_ldap_name(s12_processing_by)
                    w12 = WorkflowCitesType()
                    w12.node_code = '12-processed'
                    w12.node_name = 'žádost zpracována'
                    w12.responsible = None
                    w12.date_execution = s12_date_processing
                    w12.executor = UserType(dn=ldap_name, name=cn)
                    w12.status_from = '11-accepted'
                    w12.status_to = '12-processed'
                    status = w12.node_code
                    self.entries.append(w12)
            else:
                if s3_date_delivered is not None:
                    cn, ldap_name = parse_ldap_name(s3_delivered_by)
                    w3 = WorkflowCitesType()
                    w3.node_code = '3-delivered'
                    w3.node_name = f'doručeno podatelnou pod čj. CE {id_no}, čj. {id_local}'
                    w3.responsible = None
                    # date_execution=s3_date_delivered.strftime('%Y-%m-%dT%H:%M:%SZ')
                    w3.date_execution = s3_date_delivered
                    w3.executor = UserType(dn=ldap_name, name=cn)
                    w3.status_from = '2-authorized'
                    w3.status_to = '4-processing'
                    status = w3.node_code
                    self.entries.append(w3)
                if s4_date_processing is not None:
                    cn, ldap_name = parse_ldap_name(s4_processing_by)
                    w4 = WorkflowCitesType()
                    w4.node_code = '4-processing'
                    w4.node_name = 'vyřizuje se'
                    w4.responsible = None
                    # date_execution=s4_date_processing.strftime('%Y-%m-%dT%H:%M:%SZ')
                    w4.date_execution = s4_date_processing
                    w4.executor = UserType(dn=ldap_name, name=cn)
                    w4.status_from = '3-delivered'
                    w4.status_to = '5-statement'
                    status = w4.node_code
                    self.entries.append(w4)
                if s5_date_statement_request is not None:
                    cn, ldap_name = parse_ldap_name(s5_statement_request_by)
                    w5 = WorkflowCitesType()
                    w5.node_code = '5-statement'
                    w5.node_name = 'vyřizuje se (požadavek na stanovisko)'
                    w5.responsible = None
                    # w5.date_execution=s5_date_statement_request.strftime('%Y-%m-%dT%H:%M:%SZ')
                    w5.date_execution = s5_date_statement_request
                    w5.executor = UserType(dn=ldap_name, name=cn)
                    w5.status_from = '4-processing'
                    w5.status_to = '6-processed'
                    status = w5.node_code
                    self.entries.append(w5)
                if s6_date_processed is not None:
                    cn, ldap_name = parse_ldap_name(s6_processed_by)
                    w6 = WorkflowCitesType()
                    w6.node_code = '6-processed'
                    w6.node_name = 'vyřízeno'
                    w6.responsible = None
                    w6.date_execution = s6_date_processed
                    w6.executor = UserType(dn=ldap_name, name=cn)
                    w6.status_from = '5-statement'
                    w6.status_to = None
                    status = w6.node_code
                    self.entries.append(w6)
                if s7_date_approved is not None:
                    cn, ldap_name = parse_ldap_name(s7_approved_by)
                    w7 = WorkflowCitesType()
                    w7.node_code = '7-approved'
                    w7.node_name = 'schváleno'
                    w7.responsible = None
                    w7.date_execution = s7_date_approved
                    w7.executor = UserType(dn=ldap_name, name=cn)
                    w7.status_from = '2-authorized'
                    w7.status_to = None
                    status = w7.node_code
                    self.entries.append(w7)
                if s8_date_in_process is not None:
                    cn, ldap_name = parse_ldap_name(s8_in_process_by)
                    w8 = WorkflowCitesType()
                    w8.node_code = '3-in_process'
                    w8.node_name = 'zpracovává se'
                    w8.responsible = None
                    w8.date_execution = s8_date_in_process
                    w8.executor = UserType(dn=ldap_name, name=cn)
                    w8.status_from = '2-authorized'
                    w8.status_to = None
                    status = w8.node_code
                    self.entries.append(w8)
                if s9_date_statement_issued is not None:
                    cn, ldap_name = parse_ldap_name(s9_statement_issued_by)
                    w9 = WorkflowCitesType()
                    w9.node_code = '4-statement_issued'
                    w9.node_name = 'vydáno stanovisko'
                    w9.responsible = None
                    w9.date_execution = s9_date_statement_issued
                    w9.executor = UserType(dn=ldap_name, name=cn)
                    w9.status_from = '3-in_process'
                    w9.status_to = None
                    status = w9.node_code
                    self.entries.append(w9)
                if rejected:
                    cn, ldap_name = parse_ldap_name(s99_rejected_by)
                    w99 = WorkflowCitesType()
                    w99.node_code = '99-rejected'
                    w99.node_name = 'zamítnuto'
                    w99.responsible = None
                    w99.date_execution = s99_date_rejected
                    w99.executor = UserType(dn=ldap_name, name=cn)
                    w99.status_from = None
                    w99.status_to = None
                    status = w99.node_code
                    self.entries.append(w99)
        if status is None:
            status = get_dict_value(data, 'status')
        self.count = len(self.entries)
        self.status = status
        return self


class TransportType(BaseModel):
    vehicle: Optional[str] = Field(default=None, description='dopravní porstředek')
    border: Optional[str] = Field(default=None, description='hraniční přechod')
    date_transit: Optional[datetime] = Field(default=None, description='datum přechodu hranice', examples=['2021-08-30T23:01:14.274085491+15:55'])


class EntryType(MetadataType):
    doc_code: Optional[str] = Field(
        default=None,
        description='Kód dokumentu - vazba na šablony',
        examples=['DD01'],
    )
    doc_class: Optional[str] = Field(
        default=None,
        description="Třída dokumentu: ['DocumentPrincipalType', 'DocumentRegistrationCardType'] \n",
        examples=['DocumentPrincipalType'],
    )
    date_issued: Optional[datetime] = Field(
        default=None,
        description='Datum vydání dokumentu',
        examples=['2021-08-30T23:01:14.274085491+15:55'],
    )

# verze 1.1.0 --------------------------------------------------------------------------

class AdditionalType(BaseModel):
    special_conditions: Optional[str] = Field(default=None, description='Nějaký HTML text pro AOPK')
    fertility: Optional[int] = Field(default=None, description='maximální možná plodnost jednoho exempláře')


class HybridType(BaseModel):
    name: Optional[str] = Field(default=None, description='Název křížence')
    source: Optional[List[str]] = Field(default=None, description='Seznam vědeckých názvů zdrojových druhů')
    comment: Optional[str] = Field(default=None, description='Popis křížence')


class Regulation449Enum(BaseEnum):
    A = 'A'
    B = 'B'
    EMPTY = ''


class RegulationCitesEnum(BaseEnum):
    I = 'I'
    I_II = 'I/II'
    II = 'II'
    II_III = 'II/III'
    III = 'III'
    NC = 'NC'
    Not_CITES_114_1992 = 'Not CITES. Protected by the Act 114/1992.'
    Not_CITES = 'Not CITES'
    EMPTY = ''


class RegulationEuEnum(BaseEnum):
    A = 'A'
    A_B = 'A/B'
    B = 'B'
    B_D = 'B/D'
    C = 'C'
    D = 'D'
    EMPTY = ''


class PublishedEnum(BaseEnum):
    NOT_PUBLISHED = '0'
    PUBLISHED = '1'
    ALL = 'all'


class ThreeStateEnum(BaseEnum):
    FALSE = '0'
    TRUE = '1'
    ALL = 'all'


class DocumentCodeEnum(BaseEnum):
    DD01 = 'DD01'   # Potvrzení o přemístění exempláře
    DD02 = 'DD02'   # Potvrzení o původu
    DD03 = 'DD03'   # Potvrzení vlastnictví
    DD04 = 'DD04'   # Potvrzení o putovní výstavě
    DD05 = 'DD05'   # Potvrzení o souboru vzorků
    DD06 = 'DD06'   # Potvrzení o hudebním nástroji
    DD07 = 'DD07'   # Potvrzení legality získání exempláře
    DD08 = 'DD08'   # Žádost o permit
    DD09 = 'DD09'   # Permit
    DD10 = 'DD10'   # Žádost o potvrzení (o zákonném získání, pro obchodní činnosti, pro přemístění živých exemplářů)
    DD11 = 'DD11'   # Žádost o potvrzení o putovní výstavě
    DD12 = 'DD12'   # Registrační list
    DD13 = 'DD13'   # Žádost o registrační list
    DD14 = 'DD14'   # Potvrzení o výjimce z obchodování
    DD15 = 'DD15'   # Souhrnná žádost o RL/Potvrzení o výjimku

    AD01 = 'AD01'   # Dodatečný záznam
    AD02 = 'AD02'   # Osobní záznam
    AD03 = 'AD03'   # Odhlášení exempláře
    AD04 = 'AD04'   # Změna držitele
    AD05 = 'AD05'   # Zrušení

    EX011 = 'EX011' # Evidenční karta k žádosti o permit

    ST01 = 'ST01'   # Stanovisko AOPK k permitu
    ST02 = 'ST02'   # Žádost o stanovisko k výjimce
    ST03 = 'ST03'   # Stanovisko k výjimce

    OD005 = 'OD005' # Obrazová příloha výjimky
    OD006 = 'OD006' # Obrazová příloha registračního listu

# Dodatečné záznamy --------------------------------------------------------------------

class AdditionalTypeEnum(BaseEnum):
    ADDITIONAL = 'additionalRecord'
    PERSONAL = 'personalRecord'
    HOLDER_CHANGE = 'holderChange'
    HOLDER_CHECKOUT = 'holderCheckout'
    DISCARD = 'discard'

    @classmethod
    def form_to_doc(cls, form):
        """
        Na základě názvu formuláře vrací tuple (kód dokumentu, 'název dokumentu))
        doc_code, title = AdditionalTypeEnum.form_to_doc(form)

        :param form:    Název formuláře
        :return:    tuple
        """
        try:
            t = cls(form)
            out = ADDITIONAL_DOC_CODE[t]
            return out
        except ValueError:
            return None, None


class GoodsIdentificationChangeEnum(BaseEnum):
    NEW = 'N'
    CHANGE = 'CH'
    RECALL = 'R'


class DiscardEnum(BaseEnum):
    # důvod zrušení (D - úhyn, E - vývoz, OR - jiný důvod)
    DEATH = 'D'
    EXPORT = 'E'
    OTHER = 'OR'
    UNKNOWN = ''


class AdditionalEntryType(MetadataType):
    doc_code: Optional[str] = Field(
        None,
        description='Kód dokumentu z číselníku - vazba na formuláře PDF',
        examples=['DD01'],
    )
    doc_class: Optional[str] = Field(
        None,
        description="Třída dokumentu: ['DocumentAdditionalType'] \n",
        examples=['DocumentPrincipalType'],
    )
    parent: Optional[RelatedType] = None
    date_issued: Optional[datetime] = Field(
        None,
        description='Datum vydání dokumentu',
        examples=['2021-08-30T23:01:14.274085491+15:55'],
    )



ADDITIONAL_DOC_CODE = {
    AdditionalTypeEnum.ADDITIONAL: ('AD01', 'Dodatečný záznam'),
    AdditionalTypeEnum.PERSONAL: ('AD02', 'Osobní záznam'),
    AdditionalTypeEnum.HOLDER_CHECKOUT: ('AD03', 'Odhlášení vlastníka'),
    AdditionalTypeEnum.HOLDER_CHANGE: ('AD04', 'Změna vlastníka'),
    AdditionalTypeEnum.DISCARD: ('AD05', 'Vyřazení z registru'),
}


# STATEMENTS ==================================================

class IntentEnum(BaseEnum):
    # Účel výjimky
    A = 'a'
    C = 'c'
    D = 'd'
    E = 'e'
    F = 'f'
    G = 'g'
    H = 'h'
    EMPTY = ''


class ExceptionTypeEnum(BaseEnum):
    # Druh výjimky (na transakci|T, na exemplář|E)
    TRANSACTION = 'T'
    SPECIES = 'E'
    EMPTY = ''


class AgreeKeyEnum(BaseEnum):
    # Notes pole Agree (Souhlas|1, Nesouhlas|0, Jiné|X)
    APPROVE = '1'
    REJECT = '0'
    OTHER = 'X'
    EMPTY = ''


class AgreeValueEnum(BaseEnum):
    """
    Notes pole Agree_values:
        1. Transakce nebude mít škodlivý účinek na stav zachování dotčeného druhu ani na rozsah území, na kterém se příslušná populace daného druhu vyskytuje.
        2. Nejsou známy žádné další okolnosti týkající se zachování dotčeného druhu, které mluví proti vydání povolení nebo potvrzení.
        3. Místo určení, kde má být živý exemplář umístěn, je vybaveno tak, že umožňuje ochranu exempláře a řádnou péči o něj.
    """
    VALUE_1 = '1'
    VALUE_2 = '2'
    VALUE_3 = '3'
    VALUE_EMPTY = ''

AGREE_VALUES = {
    AgreeValueEnum.VALUE_EMPTY: '',
    AgreeValueEnum.VALUE_1: '1. Transakce nebude mít škodlivý účinek na stav zachování dotčeného druhu ani na rozsah území, na kterém se příslušná populace daného druhu vyskytuje.',
    AgreeValueEnum.VALUE_2: '2. Nejsou známy žádné další okolnosti týkající se zachování dotčeného druhu, které mluví proti vydání povolení nebo potvrzení.',
    AgreeValueEnum.VALUE_3: '3. Místo určení, kde má být živý exemplář umístěn, je vybaveno tak, že umožňuje ochranu exempláře a řádnou péči o něj.'
}

class AgreeType(BaseModel):
    key: Optional[AgreeKeyEnum] = Field(
        default=None,
        description='Notes pole Agree (Souhlas|1, Nesouhlas|0, Jiné|X)',
        examples=['1'],
    )
    value_list: Optional[List[AgreeValueEnum]] = Field(
        default=None,
        description="""Notes pole Agree_values: <br>1. Transakce nebude mít škodlivý účinek na stav zachování dotčeného druhu ani na rozsah území, na kterém se příslušná populace daného druhu vyskytuje. <br>2. Nejsou známy žádné další okolnosti týkající se zachování dotčeného druhu, které mluví proti vydání povolení nebo potvrzení. <br>3. Místo určení, kde má být živý exemplář umístěn, je vybaveno tak, že umožňuje ochranu exempláře a řádnou péči o něj.\n""",
        examples=['1', '2', '3']
    )
