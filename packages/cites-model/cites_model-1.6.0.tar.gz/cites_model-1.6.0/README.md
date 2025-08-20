# Datový model CITES

Projekt obsahuje knihovnu Python s kompletním datovým modelem CITES

## Verze 1

V této verzi jsou implementovány tyto třídy: 

### cites_common

Třídy pro obecné použití rozšířené pro CITES

1. BaseEntryListType
2. BirthTypeEnum
3. CertifiedEnum
4. ConditionsType
5. DeliveryEnum
6. DocumentPrincipalCustomsGoodsType
7. DocumentPrincipalCustomsPermitType
8. EntryType
9. GeneralType
10. GoodsBirthType
11. GoodsIdetificationHistoryItemType
12. GoodsIdetificationType
13. GoodsItemBaseType
14. GoodsOrderType
15. GoodsPrincipalType
16. GoodsQuantityType
17. IssuingPurposeEnum
18. IssuingType
19. MailAddressType
20. MetricEnum
21. OtherType
22. PermitSpecialConditionsType
23. PermitTypeEnum
24. PersonExtendedType
25. PersonHistoryItemType
26. PersonTypeEnumDeprecated (1.3.1)
27. PhoneNumberType
28. RelatedType
29. TaxonItemType
30. TransactionType
31. TransportType
32. ValidityEnum
33. WorkflowCitesType
34. WorkflowListType

Ve verzi 1.1 přidáno

1. AdditionalType
2. HybridType
3. PublishedEnum
4. Regulation449Enum
5. RegulationCitesEnum
6. RegulationEuEnum

Ve verzi 1.3 přidáno

1. AdditionalTypeEnum
2. GoodsIdentificationChangeEnum
3. DiscardEnum
4. AdditionalEntryType
5. ADDITIONAL_DOC_CODE (dict)


### cites_document

Základní dokumenty CITES

1. CitesDocumentEntryListType
2. CitesDocumentPrincipalType
3. CitesDocumentPrincipalTypeWrite


### cites_reg_card

Evidenční list CITES CZ

1. CitesDocumentRegistrationCardType
2. CitesDocumentRegistrationCardTypeWrite

### cites_swin

1. SingleWindowType

### cites_taxon

Od verze 1.1

1. TaxonEntryListType
2. TaxonEntryType
3. TaxonType

## UUID

Třída UUID se nepoužívá Byla nahrazena běžným textem, protože jsou potíže se zálohovánmím dat 
při nativním ukládání UUID do MongoDb. 

## Verze 1.2

### cites_template

1. TemplateTypeEnum
2. TemplateBaseType
3. TemplateFullType


## Verze 1.3

### cites_additional

1. CitesDocumentAdditionalEntryListType
2. CitesDocumentAdditionalType
3. CitesDocumentAdditionalTypeWrite

## Verze 1.3.3

Přidáno **TaxonType.is_active** a **ThreeStateEnum**

## Verze 1.3.5

Přesunuto do nového repozitáře: https://github.com/SYSNET-CZ/models 


## Verze 1.4.

### customs_permit

1. CustomsExchangeCitesGoodsType
2. CustomsExchangeCitesPermitType

Včetně konverzních (mapovacích) metod z produkčního modelu _CustomsExchangeCitesPermitType_ a _CitesDocumentPrincipalType_ 

## Verze 1.5

1. Do hlavních dokumentů a zboží doplněn atribut **history**. Slouží pro ukládání logů týkajících se objektu. 
2. Do třídy **OtherType** doplněny položky obsahující údaje pro žádost o RL/CERT


## Verze 1.5.9

Zvýšena minimální verze sysnet-pyutils na 1.3.10 https://pypi.org/project/sysnet-pyutils/1.3.10/ 
(Do **MetadataTypeBase** doplněn atribut **comment**)


## Verze 1.6

Přidán balíček **cites_statement** obsahující třídy pro stanoviska AOPK
