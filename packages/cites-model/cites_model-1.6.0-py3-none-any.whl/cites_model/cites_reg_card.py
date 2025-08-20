from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel, Field
from sysnet_pyutils.models.general import MetadataTypeBase, LinkedType, MetadataType

from cites_model.cites_common import PersonExtendedType, TransportType, DeliveryEnum, IssuingType


class CitesDocumentRegistrationCardTypeWrite(BaseModel):
    applicant: Optional[PersonExtendedType] = None
    applicant_agent: Optional[PersonExtendedType] = None
    exception_114: Optional[str] = Field(
        default=None,
        description='Týká-li se žádost jedinců zvláště chráněných živočichů nebo rostlin podle zákona č. 114/1992 Sb., o ochraně přírody a krajiny, přiložte kopii udělené výjimky, případně uveďte, že výjimka nebyla udělena a proč\n',
    )
    exception_23: Optional[str] = Field(
        default=None,
        description='Týká-li se žádost jedinců zvláště chráněných živočichů nebo rostlin podle zákona č. 114/1992 Sb., o ochraně přírody a krajiny, přiložte kopii udělené výjimky, případně uveďte, že výjimka nebyla udělena a proč\n',
    )
    exception_338: Optional[str] = Field(
        default=None,
        description='Týká-li se žádost exemplářů, pro které bylo vydáno potvrzení o výjimce ze zákazu obchodních činností podle článku 8 odst. 3 nařízení Rady (ES) č. 338/97, přiložte toto potvrzení nebo jeho kopii, případně uveďte, že potvrzení nebylo vydáno a proč\n',
    )
    owner_change: Optional[bool] = Field(
        default=None,
        description='Znamená plánovaný vývoz, zpětný vývoz, dovoz nebo přemístění exempláře změnu majitele exempláře?\n',
    )
    destination: Optional[str] = Field(
        default=None,
        description='Pro případ žádosti o povolení přemístění exempláře v rámci ČR nebo EU, uveďte podrobnosti a zdůvodnění pro nové místo určení exempláře\n',
    )
    transport_out: Optional[TransportType] = Field(default=None, description='Způsob dopravy při dovozu')
    transport_in: Optional[TransportType] = Field(default=None, description='Způsob dopravy při vývozu')
    confirmer: Optional[str] = Field(
        default=None,
        description='Osoby nebo organizace, které mohou potvrdit Vámi uvedené údaje. Např. úřad, kde jste registrován, zájmová organizace, obchodní organizace, které dodáváte své produkty, apod. Uveďte adresu, telefon, fax, e-mail apod.\n',
    )
    additional: Optional[str] = Field(
        default=None,
        description='K žádosti a této evidenční kartě jsou připojeny následující dokumenty. (Zřetelně označte doklady, které chcete po vyřízení vrátit zpět.)\n',
    )
    delivery: Optional[DeliveryEnum] = Field(
        default=None,
        description='Vyřízené povolení nebo potvrzení (nehodící se škrtne)  vyzvednu osobně/ chci zaslat poštou na adresu\n',
    )
    delivery_address: Optional[str] = Field(default=None, description='Doručovací adresa')
    note: Optional[str] = Field(default=None, description='Poznámka')
    comment: Optional[str] = Field(default=None, description='Obecná poznámka')
    issuing: Optional[IssuingType] = Field(default=None, description='Údaje o vydání')
    metadata: Optional[MetadataTypeBase] = Field(default=None, description='Zapisovaná metadata dokumentu')
    # attachments: Optional[List[AttachmentType]] = None
    linked_list: Optional[List[Optional[LinkedType]]] = Field(default=None, description='Seznam provázaných dokumentů')


class CitesDocumentRegistrationCardType(CitesDocumentRegistrationCardTypeWrite):
    doc_code: str = Field(default='EX011', description='Kód dokumentu - vazba na šablonu')
    metadata: Optional[MetadataType] = Field(default=None, description='Úplná metadata dokumentu')
    history: Optional[List[Optional[str]]] = Field(default=None, description='Historie dokumentu ($History)')

