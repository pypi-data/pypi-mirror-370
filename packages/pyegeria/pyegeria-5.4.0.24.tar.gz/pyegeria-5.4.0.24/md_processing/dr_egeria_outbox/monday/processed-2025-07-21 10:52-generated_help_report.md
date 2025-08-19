y# Dr.Egeria Command Reference

This document contains the descriptions of all Dr.Egeria commands currently defined.


# Term List for search string: `*`

# Term Report - created at 2025-07-21 10:52
	Term  found from the search string:  `All`

<a id="37d9a31e-bd4b-4a56-a42c-a57b8b7e7a7b"></a>
# Term Name: Create Information Supply Chain

## GUID
37d9a31e-bd4b-4a56-a42c-a57b8b7e7a7b

## Description
The flow of a particular type of data across a digital landscape.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  |
| Description | False | True | False | None | A description of the data structure. | False |  |
| Scope | False | True | False | None | Scope of the supply chain. | False |  |
| Purposes | False | True | False | None | A list of purposes. | False |  |
| Nested Information Supply Chains | False | True | False | None | A list of supply chains that compose this supply chain. | False |  |
| In Information Supply Chain | False | True | False | None | Supply chains that this supply chain is in. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |
| Merge Update | False | True | False | None | If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None. | False |  |

## Qualified Name
Term::Create Information Supply Chain

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="14cefdf9-8cb6-4be9-a5e4-38648f26199c"></a>
# Term Name: Attach Collection->Resource

## GUID
14cefdf9-8cb6-4be9-a5e4-38648f26199c

## Description
Connect an existing collection to an element using the ResourceList relationship.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Collection | True | True | False | None | An element of base type collection (e.g. collection, agreement; subscription, ...) | False |  |
| Resource | True | True | False | None | The name of the resource to attach to. | False |  |
| Resource Use | False | True | False | None | Describes the relationship between the resource and the collection. | False |  |
| Resource Description | False | True | False | None | A description of the resource being attached. | False |  |
| Resource Use Properties | False | True | False | None | A dictionary of name:value pairs describing properties of the resource use. | False |  |

## Qualified Name
Term::Attach Collection->Resource

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="6f68b434-2853-4433-9484-a44e6e93f074"></a>
# Term Name: Create Data Dictionary

## GUID
6f68b434-2853-4433-9484-a44e6e93f074

## Description
A Data Dictionary is an organized and curated collection of data definitions that can serve as a reference for data professionals

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Dictionary | False |  |
| Description | False | True | False | None | A description of the Data Dictionary. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Data Dictionary

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="9a98e18b-53fc-4110-a777-c9d86db520fa"></a>
# Term Name: Create Agreement

## GUID
9a98e18b-53fc-4110-a777-c9d86db520fa

## Description
A kind of collection that represents an Agreement. This is for generic agreements. Specific kinds of agreements have their own commands.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  agreement. | False |  |
| Description | False | True | False | None | Description of the contents of the agreement. | False |  |
| Agreement Identifier | False | True | False | None | A user specified agreement identifier. | False |  |
| Agreement Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Version Identifier | False | True | False | None | Published agreement version identifier. | False |  |
| Agreement Actors | False | True | False | None | A list of actors with responsibilities for the agreement. | False |  |
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  |
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  |
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  |
| Usage Measurements | False | True | False | None | A dictionary of property:value pairs describing usage measurements. | False |  |
| Product Metrics | False | True | False | None | A dictionary of property:value pairs describing metrics for the product/. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Agreement

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="676939eb-be4a-4fd3-9a9f-a23152a1ef07"></a>
# Term Name: Create Data Specification

## GUID
676939eb-be4a-4fd3-9a9f-a23152a1ef07

## Description
A Data Specification defines the data requirements for a project or initiative. This includes the data structures , data fields and data classes.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Specification. | False |  |
| Description | False | True | False | None | A description of the Data Specification. | False |  |
| Collection Type | False | True | False | None | A user supplied collection type. | False |  |
| Qualified Name | True | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Data Specification

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="22089aef-39a3-479d-833b-801e6923d6cb"></a>
# Term Name: Facility

## GUID
22089aef-39a3-479d-833b-801e6923d6cb

## Summary
The facility type captures a particular type of operation that Coco Pharmaceuticals has running at one of its sites.

## Description
Each type of facility, such as manufacturing, research, offices, ..., needs different equipment and are likely to have different sustainability challenges.  Therefore by breaking down the activity at each site into facilities, it is possible to create a separate focus on each type of facility.

## Qualified Name
GlossaryTerm:Facility

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="1d4168d5-680d-4b97-a155-7af2399a2dab"></a>
# Term Name: Create Regulation Article

## GUID
1d4168d5-680d-4b97-a155-7af2399a2dab

## Description
A RegulationArticle entity is an article in a regulation. Dividing a regulation  simplifies planning and execution.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Regulation Article

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="ffe5155b-cb74-4642-ad55-4e3a7af9d3ef"></a>
# Term Name: Measurement Date

## GUID
ffe5155b-cb74-4642-ad55-4e3a7af9d3ef

## Summary
The date that the patient measurement was made.

## Description
The measurements are from a discrete day so that any changes in a patient''s condition can be measured.  The format of the date may vary depending on the source of the measurement.

## Usage
Used to identify the data of any patient measurement during a clinical trial.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::MeasurementDate

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Clinical Trials Common Data Fields


---

<a id="261821ea-1552-4279-9207-dea6dfe9aa57"></a>
# Term Name: Create Business Imperative

## GUID
261821ea-1552-4279-9207-dea6dfe9aa57

## Description
The BusinessImperative entity defines a business goal that is critical to the success of the organization.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Business Imperative

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="a4438b93-a5c1-4b3f-9b3e-1c673edaf457"></a>
# Term Name: View Solution Components

## GUID
a4438b93-a5c1-4b3f-9b3e-1c673edaf457

## Description
Return the data structure details, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict |
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  |

## Qualified Name
Term::View Solution Components

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="8dab28e9-c0da-4117-bb57-15d07c30e83e"></a>
# Term Name: Create Governance Approach

## GUID
8dab28e9-c0da-4117-bb57-15d07c30e83e

## Description
The GovernanceApproach entity defines a policy that describes a method that should be used for a particular activity.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Governance Drivers | False | True | False | None | The drivers this policy is in response to. Drivers may be Business Imperatives, Regulations, Governance Strategy or Threats. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Approach

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="a0fc06f8-cd2b-4205-af30-51916bf9975e"></a>
# Term Name: Patient Height

## GUID
a0fc06f8-cd2b-4205-af30-51916bf9975e

## Summary
Template Substitute for Patient Height

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::PatientHeight

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="fccd6393-030f-45b8-b2ce-de6d857e8fa1"></a>
# Term Name: Link Governance Controls

## GUID
fccd6393-030f-45b8-b2ce-de6d857e8fa1

## Description
Link peer governance controls with the GovernanceControlLink relationship. Controls types are: GovernanceRule, GovernanceProcess, GovernanceResponsibility, GovernanceProcedure, SecurityAccessControl, SecurityGroup.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Control Definition 1 | True | True | False | None | The  first governance control to link. | False |  |
| Control Definition 2 | True | True | False | None | The  fsecond governance control to link. | False |  |
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  |
| Description | False | True | False | None | A description of the relationship. | False |  |

## Qualified Name
Term::Link Governance Controls

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="0c8af67f-3a0a-48ec-a245-38da23b2c927"></a>
# Term Name: Greenhouse Gas Protocol

## GUID
0c8af67f-3a0a-48ec-a245-38da23b2c927

## Summary
The Greenhouse Gas Protocol set the standards to measure and manage harmful emissions.

## Description
GHG Protocol establishes comprehensive global standardized frameworks to measure and manage greenhouse gas (GHG) emissions from private and public sector operations, value chains and mitigation actions.
Building on a 20-year partnership between World Resources Institute (WRI) and the World Business Council for Sustainable Development (WBCSD), GHG Protocol works with governments, industry associations, NGOs, businesses and other organizations.

## Qualified Name
GlossaryTerm:Greenhouse Gas Protocol

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="b4765468-4c70-42ec-b4fa-51e9e14193c0"></a>
# Term Name: View Information Supply Chains

## GUID
b4765468-4c70-42ec-b4fa-51e9e14193c0

## Description
Return information supply chains filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; MD; REPORT; MERMAID; LIST; DICT; HTML |
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  |

## Qualified Name
Term::View Information Supply Chains

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="aff97a9a-45dd-4292-9ecc-2dece60d8a07"></a>
# Term Name: View Data Structures

## GUID
aff97a9a-45dd-4292-9ecc-2dece60d8a07

## Description
Return the data structures, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict |
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  |
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  |
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  |
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  |
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING |
| Page Size | False | True | False | None | The number of elements returned per page. | False |  |
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  |

## Qualified Name
Term::View Data Structures

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="4e230607-f47f-44ea-b696-2a49392f231b"></a>
# Term Name: Create Solution Role

## GUID
4e230607-f47f-44ea-b696-2a49392f231b

## Description
A collection of data fields that for a data specification for a data source.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Name | True | True | False | None | Name of the role. | False |  |
| Description | False | True | False | None | A description of the data structure. | False |  |
| Title | False | True | False | None | Title of the role. | False |  |
| Scope | False | True | False | None | Scope of the role. | False |  |
| identifier | False | True | False | None | role identifier | False |  |
| Domain Identifier | False | True | False | None | Governance domain identifier | False |  |
| Role Type | False | True | False | None | Type of the role.  Currently must be GovernanceRole. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Solution Role

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="a451035c-34c8-4ce1-b7e5-c8368cf235c1"></a>
# Term Name: Create DigitalSubscription

## GUID
a451035c-34c8-4ce1-b7e5-c8368cf235c1

## Description
A type of agreement for a digital subscription.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  agreement. | False |  |
| Description | False | True | False | None | Description of the contents of the agreement. | False |  |
| Identifier | False | True | False | None | A user specified agreement identifier. | False |  |
| Product Status | False | True | False | None | The status of the digital product. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User_Defined_Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Support Level | False | True | False | None | Level of support agreed or requested. | False |  |
| Service Levels | False | True | False | None | A dictionary of name:value pairs describing the service levels. | False |  |
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  |
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  |
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  |
| Usage Measurements | False | True | False | None | A dictionary of property:value pairs describing usage measurements. | False |  |
| Product Metrics | False | True | False | None | A dictionary of property:value pairs describing metrics for the product/. | False |  |
| Version Identifier | False | True | False | None | Published agreement version identifier. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create DigitalSubscription

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="87d28d7c-4d8a-45b8-abbc-9973002283a7"></a>
# Term Name: CO2 Emission Scope

## GUID
87d28d7c-4d8a-45b8-abbc-9973002283a7

## Summary
A type of activity that produces CO2.

## Description
One aspect of sustainability is to reduce the amount of CO2 that is produced by the organization. The GHG protocol divides the reporting of CO2 emissions into three scopes: Scope 1, Scope 2 and Scope 3, to make it easier to monitor and build plans to reduce emissions.

## Qualified Name
GlossaryTerm:CO2 Emission Scope

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="e00384cd-616e-4707-9917-8f95ec41dabf"></a>
# Term Name: Link Agreement Items

## GUID
e00384cd-616e-4707-9917-8f95ec41dabf

## Description
Attach or detach an agreement to an element referenced in its definition. Agreement item can be an referenced element.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Description | False | True | False | None | Description of the contents of the agreement item. | False |  |
| Agreement Item Id | False | True | False | None | A user specified agreement item identifier. | False |  |
| Agreement Start | False | True | False | None | The start date of the agreement as an ISO 8601 string. | False |  |
| Agreement End | False | True | False | None | The end date of the agreement as an ISO 8601 string. | False |  |
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  |
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  |
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  |
| Usage Measurements | False | True | False | None | A dictionary of property:value pairs describing usage measurements. | False |  |
| Usage Metrics | False | True | False | None | A dictionary of property:value pairs describing usage metrics for the agreements. | False |  |

## Qualified Name
Term::Link Agreement Items

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="dd68ca33-a3c3-46b6-befe-142ea0aa9210"></a>
# Term Name: Attach Term-Term Relationship

## GUID
dd68ca33-a3c3-46b6-befe-142ea0aa9210

## Description
Create a relationship between terms.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Term  1 | True | True | False | None | The name of the first term term to connect. | False |  |
| Term  2 | True | True | False | None | The name of the second term term to connect. | False |  |
| Relationship | True | True | False | None | The type of relationship to connecting the two terms. | False | Synonym;  Translation;  PreferredTerm; TermISATYPEOFRelationship;  TermTYPEDBYRelationship;  Antonym; ReplacementTerm;  ValidValue; TermHASARelationship; RelatedTerm;   ISARelationship |

## Qualified Name
Term::Attach Term-Term Relationship

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="9fb34e8e-72f1-4478-b65a-a745c8e51a66"></a>
# Term Name: Create Governance Process

## GUID
9fb34e8e-72f1-4478-b65a-a745c8e51a66

## Description
An executable process that choreographs different actions.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Process

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="c6a0f97f-6a2e-42b0-b7e4-cdeada0a0fc4"></a>
# Term Name: Patient Blood Pressure

## GUID
c6a0f97f-6a2e-42b0-b7e4-cdeada0a0fc4

## Summary
Blood pressure of patient (systolic and diastolic).

## Description
Blood pressure is the pressure of circulating blood against the walls of blood vessels. Most of this pressure results from the heart pumping blood through the circulatory system. Blood pressure is expressed in terms of the systolic pressure over diastolic pressure in the cardiac cycle. It is measured in millimetres of mercury above the surrounding atmospheric pressure, or in kilopascals. The difference between the systolic and diastolic pressures is known as pulse pressure, while the average pressure during a cardiac cycle is known as mean arterial pressure.

## Usage
Acts as one of the standard mechanism for measuring the health of a patient in a clinical trial.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::PatientBloodPressure

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Clinical Trials Common Data Fields


---

<a id="21e8878d-b550-49a6-b3f3-ca5d4fab4ba5"></a>
# Term Name: Create Governance Obligation

## GUID
21e8878d-b550-49a6-b3f3-ca5d4fab4ba5

## Description
The GovernanceObligation entity defines a policy that describes a requirement that must be met.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Governance Drivers | False | True | False | None | The drivers this policy is in response to. Drivers may be Business Imperatives, Regulations, Governance Strategy or Threats. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Obligation

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="4cdbb398-dd73-4342-8d76-2360120d73ba"></a>
# Term Name: Create Service Level Objectives

## GUID
4cdbb398-dd73-4342-8d76-2360120d73ba

## Description
Defines the performance, availability and qualitiy levels expected by the element attached.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Service Level Objectives

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="363a54e0-2196-4d1c-b153-c10dc58440e1"></a>
# Term Name: Right Hip Rotation Angle

## GUID
363a54e0-2196-4d1c-b153-c10dc58440e1

## Summary
The number of degrees of rotation of the right foot measured from vertical.

## Description
As the stuffing around the hip weakens, the foot on the attached leg rotates, typically outwards when the teddy bear is sitting.  This measurement is an integer measuring the number of degrees of rotation of the right foot measured from vertical. Positive values measure that the foot is rotating outwards.

## Usage
Definition for use in the Teddy Bear Drop Foot demonstration study.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::AngleRight

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Teddy Bear Drop Foot Data Fields


---

<a id="2549021a-de43-4e52-9881-83f482ebb9b8"></a>
# Term Name: Link Subscribers

## GUID
2549021a-de43-4e52-9881-83f482ebb9b8

## Description
Attach or detach a subscriber to a subscription. Subscriber can be any type of element.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Subscriber Id | False | True | False | None |  identifier of a subscriber. Initially, will let this be an arbitrary string - could harden this to a qualified name later if needed. | False |  |
| Agreement Start | False | True | False | None | The start date of the agreement as an ISO 8601 string. | False |  |
| Agreement End | False | True | False | None | The end date of the agreement as an ISO 8601 string. | False |  |
| Restrictions | False | True | False | None | A dictionary of property:value pairs describing restrictions. | False |  |
| Obligations | False | True | False | None | A dictionary of property:value pairs describing obligations. | False |  |
| Entitlements | False | True | False | None | A dictionary of property:value pairs describing entitlements. | False |  |
| Usage Measurements | False | True | False | None | A dictionary of property:value pairs describing usage measurements. | False |  |

## Qualified Name
Term::Link Subscribers

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="53569b49-b6ec-47f1-80a6-4f059bb3edf3"></a>
# Term Name: Create Digital Product

## GUID
53569b49-b6ec-47f1-80a6-4f059bb3edf3

## Description
A Data Dictionary is an organized and curated collection of data definitions that can serve as a reference for data professionals

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the digital product | False |  |
| Description | False | True | False | None | Description of the contents of a product. | False |  |
| Product Name | False | True | False | None | The external name of the digital product. | False |  |
| Product Status | False | True | False | None | The status of the digital product. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; APPROVED_CONCEPT; UNDER_DEVELOPMENT; DEVELOPMENT_COMPLETE; APPROVED_FOR_DEPLOYMENT; ACTIVE; DISABLED; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Product Type | False | True | False | None | Type of product - periodic, delta, snapshot, etc | False |  |
| Product Identifier | False | True | False | None | User specified product identifier. | False |  |
| Product Description | False | True | False | None | Externally facing description of the product and its intended usage. | False |  |
| Maturity | False | True | False | None | Product maturity - user defined. | False |  |
| Service Life | False | True | False | None | Estimated service lifetime of the product. | False |  |
| Introduction Date | False | True | False | None | Date of product introduction in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur. | False |  |
| Next Version Date | False | True | False | None | Date of  the next version,  in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur. | False |  |
| Withdrawal Date | False | True | False | None | Date of planned product withdrawal in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur. | False |  |
| Collection Type | False | True | False | None | A user supplied collection type. Defaults to Digital Product. | False |  |
| Current Version | False | True | False | None | Published product version identifier. | False |  |
| Product Manager | False | True | False | None | Actors responsible for managing this product. Actors may be individuals, automations, etc. | False |  |
| Agreements | False | True | False | None | A list of agreements associated with this product.  The agreements must already exist. | False |  |
| Digital Subscriptions | False | True | False | None |  | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Digital Product

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="7c0d816b-22d4-4c1a-b9a2-1028f6c654dd"></a>
# Term Name: Create Category

## GUID
7c0d816b-22d4-4c1a-b9a2-1028f6c654dd

## Description
A group of terms that are useful to collect together.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Category Name | True | True | False | None | The name of a category. | False |  |
| Description | False | True | False | None | A description of the Category. | False |  |
| In Glossary | True | True | False | None | The name of the glossary that contains the Category. Recommend using the Qualified Name of the Glossary, if known. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Category

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="8689b580-0f4a-4de5-a1cf-ce6477445946"></a>
# Term Name: Patient Identifier

## GUID
8689b580-0f4a-4de5-a1cf-ce6477445946

## Summary
Template Substitute for Patient Identifier

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::PatientId

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="ae718d8e-184f-43bb-abf7-e644e3e5bf93"></a>
# Term Name: Create Data Structure

## GUID
ae718d8e-184f-43bb-abf7-e644e3e5bf93

## Description
A collection of data fields that for a data specification for a data source.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the data structure. | False |  |
| Description | False | True | False | None | A description of the data structure. | False |  |
| In Data Specification | False | True | False | None | The data specifications this structure is a member of. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Data Structure

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="a003818e-5891-4306-9b69-a923b1261ded"></a>
# Term Name: Link Solution Component Peers

## GUID
a003818e-5891-4306-9b69-a923b1261ded

## Description
This command can be used to link or unlink wires between components.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Component1 | True | True | False | None | The  first component to link. | False |  |
| Component2 | True | True | False | None | The  second component to link. | False |  |
| Wire Label | False | True | False | None | Labels the link between two components. | False |  |
| Description | False | True | False | None | A description of the wire. | False |  |

## Qualified Name
Term::Link Solution Component Peers

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="25cc9358-9930-4b98-ac8d-4280cf87164d"></a>
# Term Name: Hydrofluorocarbon

## GUID
25cc9358-9930-4b98-ac8d-4280cf87164d

## Summary
Hydrofluorocarbons (HFCs) are man-made organic compounds that contain fluorine and hydrogen atoms, and are the most common type of organofluorine compounds.

## Description
Most HFCs are gases at room temperature and pressure. They are frequently used in air conditioning and as refrigerants; R-134a (1,1,1,2-tetrafluoroethane) is one of the most commonly used HFC refrigerants. In order to aid the recovery of the stratospheric ozone layer, HFCs were adopted to replace the more potent chlorofluorocarbons (CFCs), which were phased out from use by the Montreal Protocol, and hydrochlorofluorocarbons (HCFCs) which are presently being phased out.[1] HFCs replaced older chlorofluorocarbons such as R-12 and hydrochlorofluorocarbons such as R-21.[2] HFCs are also used in insulating foams, aerosol propellants, as solvents and for fire protection.They may not harm the ozone layer as much as the compounds they replace, but they still contribute to global warming --- with some like trifluoromethane having 11,700 times the warming potential of carbon dioxide.[3] Their atmospheric concentrations and contribution to anthropogenic greenhouse gas emissions are rapidly increasing[quantify], causing international concern about their radiative forcing.

## Qualified Name
GlossaryTerm:Hydrofluorocarbon

## Status
ACTIVE

## In Glossary
Sustainability Glossary

## Categories
Chemicals


---

<a id="53c6b0c3-31c3-460e-a4f1-f685fe5f4155"></a>
# Term Name: Link Contracts

## GUID
53c6b0c3-31c3-460e-a4f1-f685fe5f4155

## Description
Attach or detach an agreement to an element describing the location of the contract documents.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Contract Id | False | True | False | None | Contract identifier. | False |  |
| Contract Liaison | False | True | False | None | Name of the liaison for the contract. | False |  |
| Contract Liaison Type | False | True | False | None | type of liaison. | False |  |
| Contract Liaison Property Name | False | True | False | None |  | False |  |

## Qualified Name
Term::Link Contracts

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="072c6182-8004-4aee-804d-6be2afa79b9b"></a>
# Term Name: Create Solution Blueprint

## GUID
072c6182-8004-4aee-804d-6be2afa79b9b

## Description
A solution blueprint describes the architecture of a digital service in terms of solution components.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Information Supply Chain | False |  |
| Description | False | True | False | None | A description of the data structure. | False |  |
| Version Identifier | False | True | False | None | A user supplied version identifier. | False |  |
| Solution Components | False | True | False | None | Solution components that make up the blueprint. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Solution Blueprint

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="71c3a77a-110d-41d5-9637-e324ea14ee78"></a>
# Term Name: Sustainability Dashboard

## GUID
71c3a77a-110d-41d5-9637-e324ea14ee78

## Summary
Graphical summary of Coco Pharmaceuticals'' sustainability data.

## Description
The sustainability dashboard provides detailed information about the impact of the different activities undertaken by Coco Pharmaceuticals'' and how this impact is changing over time.

## Qualified Name
GlossaryTerm:Sustainability Dashboard

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="a5d62be9-49d1-4022-b1a6-2a5dbe8f657d"></a>
# Term Name: View Data Dictionaries

## GUID
a5d62be9-49d1-4022-b1a6-2a5dbe8f657d

## Description
Return the data dictionaries, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; DICT; MD; MERMAID; REPORT |
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  |
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  |
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  |
| Page Size | False | True | False | None | The number of elements returned per page. | False |  |
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  |
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  |
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING |

## Qualified Name
Term::View Data Dictionaries

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="92a5a610-78c3-404a-999f-c3352390b672"></a>
# Term Name: Carbon Dioxide

## GUID
92a5a610-78c3-404a-999f-c3352390b672

## Summary
Carbon dioxide (chemical formula CO2) is a chemical compound made up of molecules that each have one carbon atom covalently double bonded to two oxygen atoms.

## Description
Carbon dioxide is found in the gas state at room temperature, and as the source of available carbon in the carbon cycle, atmospheric CO2 is the primary carbon source for life on Earth. In the air, carbon dioxide is transparent to visible light but absorbs infrared radiation, acting as a greenhouse gas. Carbon dioxide is soluble in water and is found in groundwater, lakes, ice caps, and seawater. When carbon dioxide dissolves in water, it forms carbonate and mainly bicarbonate (HCO−3), which causes ocean acidification as atmospheric CO2 levels increase.

## Qualified Name
GlossaryTerm:Carbon Dioxide

## Status
ACTIVE

## In Glossary
Sustainability Glossary

## Categories
Chemicals


---

<a id="bafe1da9-4777-405d-b7cd-fe43615b72f9"></a>
# Term Name: Create Naming Standard Rule

## GUID
bafe1da9-4777-405d-b7cd-fe43615b72f9

## Description
A standard for naming specific kinds of resources.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  |
| Name Patterns | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Naming Standard Rule

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="9a3499e6-6b04-45e1-9b67-acd73244afc2"></a>
# Term Name: Patient Identifier

## GUID
9a3499e6-6b04-45e1-9b67-acd73244afc2

## Summary
Unique identifier of patient.

## Description
Unique identifier for the individual that has agree to take part in this study.  The identifier on its own is anonymous, preserving the privacy of the patient.  However, there is a database that ties the patient identifier to the name of the bear.

## Usage
Acts as an anonymous identifier for a patient in a clinical trial.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::PatientId

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Clinical Trials Common Data Fields


---

<a id="fc4e589c-c601-44b9-b440-cdee902f66b5"></a>
# Term Name: Left Hip Rotation Angle

## GUID
fc4e589c-c601-44b9-b440-cdee902f66b5

## Summary
The number of degrees of rotation of the left foot measured from vertical.

## Description
As the stuffing around the hip weakens, the foot on the attached leg rotates, typically outwards when the teddy bear is sitting.  This measurement is an integer measuring the number of degrees of rotation of the left foot measured from vertical. Positive values measure that the foot is rotating outwards.

## Usage
Definition for use in the Teddy Bear Drop Foot demonstration study.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::AngleLeft

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Teddy Bear Drop Foot Data Fields


---

<a id="37386623-43d8-4322-a7f3-0d27e0d35e92"></a>
# Term Name: Create Governance Procedure

## GUID
37386623-43d8-4322-a7f3-0d27e0d35e92

## Description
A manual procedure that is performed under certain circumstances.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Procedure

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="9e2b0a60-8427-4aea-8ace-97ee48addab8"></a>
# Term Name: Patient Weight

## GUID
9e2b0a60-8427-4aea-8ace-97ee48addab8

## Summary
Weight of patient in kilograms.

## Description
This is the weight of the patient in kilograms to 1 decimal place, without outer clothes on, ideally measured in the morning.

## Usage
Acts as a standard mechanism for measuring the weight of a patient in a clinical trial.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::PatientWeight

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Clinical Trials Common Data Fields


---

<a id="88489252-812d-473f-8139-000a1e21d1e2"></a>
# Term Name: Create Glossary

## GUID
88489252-812d-473f-8139-000a1e21d1e2

## Description
A grouping of definitions.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Glossary Name | True | True | False | None | The name of the glossary to create or update. | False |  |
| Description | False | True | False | None | A description of the Glossary. | False |  |
| Language | False | True | False | None | The language of the glossary. Note that multilingual descriptions are supported. Please see web site for details. | False |  |
| Usage | False | True | False | None | A description of how the glossary is to be used. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Glossary

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="cbbe56b0-1b7d-4701-8769-34af68a9862a"></a>
# Term Name: View Data Fields

## GUID
cbbe56b0-1b7d-4701-8769-34af68a9862a

## Description
Return the data fields, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; REPORT; MERMAID; DICT |
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  |
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  |
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  |
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  |
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING |
| Page Size | False | True | False | None | The number of elements returned per page. | False |  |
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  |

## Qualified Name
Term::View Data Fields

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="8e9abedc-ec1c-4030-96cd-fc33ef447eb1"></a>
# Term Name: Attach Category Parent

## GUID
8e9abedc-ec1c-4030-96cd-fc33ef447eb1

## Description
Attaches a parent category to a child category.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Category Name | True | True | False | None | The name of a category. | False |  |
| Parent Category | True | True | False | None | The name of the parent category to attach to. | False |  |

## Qualified Name
Term::Attach Category Parent

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="47eae273-01d3-464e-adf7-9a44f71fd068"></a>
# Term Name: Add Member->Collection

## GUID
47eae273-01d3-464e-adf7-9a44f71fd068

## Description
Add a member to a collection.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Element_Id | True | True | False | None | The name of the element to add to the collection. | False |  |
| Collection Id | True | True | False | None | The name of the collection to link to. There are many collection types, including Digital Products, Agreements and Subscriptions. | False |  |
| Membership Rationale | False | True | False | None | Rationale for membership. | False |  |
| Created By | False | True | False | None | Who added the member. (currently informal string) | False |  |
| Membership Status | False | True | False | None | The status of adding a member to a collection. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |

## Qualified Name
Term::Add Member->Collection

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="074f9e1c-d831-4d69-9fdb-2b362bbb132b"></a>
# Term Name: Measurement Date

## GUID
074f9e1c-d831-4d69-9fdb-2b362bbb132b

## Summary
Template Substitute for Measurement Date

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::MeasurementDate

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="26c30322-82cf-4e64-9dc9-dab1efb4eb16"></a>
# Term Name: Create Governance Rule

## GUID
26c30322-82cf-4e64-9dc9-dab1efb4eb16

## Description
An executable rule that can be deployed at particular points in the operations.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemented. | False |  |
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Rule

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="63d49bcb-f367-4b65-82e6-827145ca2d18"></a>
# Term Name: Create Governance Strategy

## GUID
63d49bcb-f367-4b65-82e6-827145ca2d18

## Description
The strategy used in the development of the governance domains activities. How the governance domain supports the business strategy.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Business Imperatives | False | True | False | None | List of imperitives. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Strategy

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="b5f1514e-7996-454d-ab7d-909487a431a0"></a>
# Term Name: View Data Classes

## GUID
b5f1514e-7996-454d-ab7d-909487a431a0

## Description
Return the data classes, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; REPORT; MERMAID; DICT |
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  |
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  |
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  |
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  |
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING |
| Page Size | False | True | False | None | The number of elements returned per page. | False |  |
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  |

## Qualified Name
Term::View Data Classes

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="40c15b4a-0123-4ca1-970f-edaaf56615d8"></a>
# Term Name: Patient Blood Pressure

## GUID
40c15b4a-0123-4ca1-970f-edaaf56615d8

## Summary
Template Substitute for Patient Blood Pressure

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::PatientBloodPressure

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="b0ae7a14-b073-4192-9933-3d5d9fed2eba"></a>
# Term Name: Link Information Supply Chain Peers

## GUID
b0ae7a14-b073-4192-9933-3d5d9fed2eba

## Description
This command can be used to link or unlink information supply chain segments.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Segment1 | True | True | False | None | The  first segment to link. | False |  |
| Segment2 | True | True | False | None | The  second segment to link. | False |  |
| Link Label | False | True | False | None | Labels the link between two information supply chain segments. | False |  |
| Description | False | True | False | None | A description of the data structure. | False |  |

## Qualified Name
Term::Link Information Supply Chain Peers

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="56cad08d-76f7-42ea-bba4-695468924e14"></a>
# Term Name: Create Governance Processing Purpose

## GUID
56cad08d-76f7-42ea-bba4-695468924e14

## Description
Privacy regulations such as  (GDPR) require data subjects to agree the processing that is permitted on their data.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Processing Purpose

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="54087c48-52b9-4b9b-9cd7-9e7f74b1e141"></a>
# Term Name: Create Governance Principle

## GUID
54087c48-52b9-4b9b-9cd7-9e7f74b1e141

## Description
The GovernancePrinciple entity defines a policy that describes an end state that the organization aims to achieve.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Governance Drivers | False | True | False | None | The drivers this policy is in response to. Drivers may be Business Imperatives, Regulations, Governance Strategy or Threats. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Principle

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="60df8a83-50da-485b-9545-c337559948d6"></a>
# Term Name: Right Hip Rotation Angle

## GUID
60df8a83-50da-485b-9545-c337559948d6

## Summary
Template Substitute for Right Hip Rotation Angle

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::AngleRight

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="e0c8920e-f472-49aa-acc6-e526214a38ac"></a>
# Term Name: Left Hip Rotation Angle

## GUID
e0c8920e-f472-49aa-acc6-e526214a38ac

## Summary
Template Substitute for Left Hip Rotation Angle

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::AngleLeft

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="cfc4354e-1a55-4ca6-87dd-3d07114ae5db"></a>
# Term Name: View Solution Roles

## GUID
cfc4354e-1a55-4ca6-87dd-3d07114ae5db

## Description
Return the data structure details, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict |
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  |

## Qualified Name
Term::View Solution Roles

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="b05e23da-f186-43d2-a34a-2c49242f3722"></a>
# Term Name: Create Certification Type

## GUID
b05e23da-f186-43d2-a34a-2c49242f3722

## Description
A type of certification.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Details | False | True | False | None | Details of the certification. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Certification Type

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="2110e000-1fa6-4d2f-912b-39421d893002"></a>
# Term Name: Link Governance Drivers

## GUID
2110e000-1fa6-4d2f-912b-39421d893002

## Description
Link peer governance drivers with the GovernanceDriverLink relationship. Drivers are: GovernanceStrategy, BusinessImperitive, Regulation, RegulationArticle, Threat.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance driver to link. | False |  |
| Definition 2 | True | True | False | None | The  second governance driver to link. | False |  |
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  |
| Description | False | True | False | None | A description of the relationship. | False |  |

## Qualified Name
Term::Link Governance Drivers

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="7bad55ba-3e76-45c3-ac45-43005223fe62"></a>
# Term Name: Create License Type

## GUID
7bad55ba-3e76-45c3-ac45-43005223fe62

## Description
A type of license.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Details | False | True | False | None | Details of the license. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create License Type

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="d85d9e01-84ec-45e9-85cc-c566be17e2b2"></a>
# Term Name: Emission

## GUID
d85d9e01-84ec-45e9-85cc-c566be17e2b2

## Summary
The release of a harmful substance into the atmosphere.

## Description
Human activity is causing the release of substances into the earth''s atmosphere that is impacting our climate and the health of the flora and fauna that we rely on to survive.  Reducing these emissions are the focus of sustainability initiatives in order to reduce the instability in the climate and availability of resources.

## Qualified Name
GlossaryTerm:Emission

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="a2f234bf-10f0-4ca1-a6a1-e975e6505704"></a>
# Term Name: Site

## GUID
a2f234bf-10f0-4ca1-a6a1-e975e6505704

## Summary
A physical location that Coco Pharmaceuticals operates from.

## Description
Coco Pharmaceuticals has a number of physical premises that is operates from.  Each of these premises is called a *site*

## Qualified Name
GlossaryTerm:Site

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="fb26ec5b-8576-49b8-ac5e-e926470426dc"></a>
# Term Name: Create Term

## GUID
fb26ec5b-8576-49b8-ac5e-e926470426dc

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Term Name | True | True | False | None | The name of the term to create or update. | False |  |
| Summary | False | True | False | None | A summary description of the term. | False |  |
| Description | False | True | False | None | A description of the term. | False |  |
| Abbreviation | False | True | False | None | An abbreviation for the term. | False |  |
| Example | False | True | False | None | An example of how the term is used. | False |  |
| Usage | False | True | False | None | A description of how the term is to be used. | False |  |
| Status | False | True | False | None | The lifecycle status of a term. | False | DRAFT; ACTIVE, DEPRECATED; OBSOLETE; OTHER |
| Published Version Identifier | False | True | False | None |  | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Term

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="2fe6262a-650d-4b8e-96a7-af9a16742c2b"></a>
# Term Name: View Governance Definitions

## GUID
2fe6262a-650d-4b8e-96a7-af9a16742c2b

## Description
This can be used to list any kind of governance definitions.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; REPORT; MERMAID; DICT |
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  |
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  |
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  |
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  |
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING |
| Order Property Name | False | True | False | None | The property to use for sorting if the sort_order_property is PROPERTY_ASCENDING or PROPERTY_DESCENDING | False |  |
| Page Size | False | True | False | None | The number of elements returned per page. | False |  |
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  |

## Qualified Name
Term::View Governance Definitions

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="336ccde3-6527-43b4-961d-28d457f8e51c"></a>
# Term Name: Link Governance Policies

## GUID
336ccde3-6527-43b4-961d-28d457f8e51c

## Description
Link peer governance policies with the GovernancePolicyLink relationship. Policies types are: GovernancePrinciple, GovernanceObligation, GovernanceApproach.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Definition 1 | True | True | False | None | The  first governance policy to link. | False |  |
| Definition 2 | True | True | False | None | The  second governance policy to link. | False |  |
| Link Label | False | True | False | None | Labels the link between two governance defninitions. | False |  |
| Description | False | True | False | None | A description of the relationship. | False |  |

## Qualified Name
Term::Link Governance Policies

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="f39544c9-0b11-4d6c-b8aa-1fe809615b24"></a>
# Term Name: Link Digital Product - Digital Product

## GUID
f39544c9-0b11-4d6c-b8aa-1fe809615b24

## Description
Link digital product dependency between two digital products.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| DigitalProduct1 | True | True | False | None | The  first product to link. | False |  |
| DigitalProduct2 | True | True | False | None | The  second product to link. | False |  |
| Label | False | True | False | None | Labels the link between two digital products. | False |  |
| Description | False | True | False | None | A description of the link. | False |  |

## Qualified Name
Term::Link Digital Product - Digital Product

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="66d3dc5e-0a50-4172-b7d0-f42715fa38f2"></a>
# Term Name: Patient Weight

## GUID
66d3dc5e-0a50-4172-b7d0-f42715fa38f2

## Summary
Template Substitute for Patient Weight

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::PatientWeight

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="513a52ad-cf8e-4b9c-b772-c6e466aafa80"></a>
# Term Name: View Solution Blueprints

## GUID
513a52ad-cf8e-4b9c-b772-c6e466aafa80

## Description
Return the data structure details, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | List; Form; Report; Dict |
| Detailed | False | True | False | None | If true a more detailed set of attributes will be returned. | False |  |

## Qualified Name
Term::View Solution Blueprints

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="371a90e8-80e7-4af2-b0ab-4d44de0fe374"></a>
# Term Name: Patient Date of Birth

## GUID
371a90e8-80e7-4af2-b0ab-4d44de0fe374

## Summary
Template Substitute for Patient Date of Birth

## Usage
Only for use in templates.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::TemplateSubstitute::PatientDateOfBirth

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Template substitutes


---

<a id="ffdcf567-5c37-4d1b-b3be-844bd995efa9"></a>
# Term Name: Create Data Sharing Agreement

## GUID
ffdcf567-5c37-4d1b-b3be-844bd995efa9

## Description
Create a new collection with the DataSharingAgreement classification.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  agreement. | False |  |
| Description | False | True | False | None | Description of the contents of the agreement. | False |  |
| Identifier | False | True | False | None | A user specified agreement identifier. | False |  |
| Agreement Status | False | True | False | None | The status of the digital product. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User_Defined_Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Version Identifier | False | True | False | None | Published agreement version identifier. | False |  |
| Product Manager | False | True | False | None | An actor responsible for managing this product. Actors may be individuals, automations, etc. | False |  |
| Digital Subscriptions | False | True | False | None |  | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Data Sharing Agreement

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="f6ac8a1d-38ca-4f33-8e39-92fcdb142d0d"></a>
# Term Name: Create Regulation Definition

## GUID
f6ac8a1d-38ca-4f33-8e39-92fcdb142d0d

## Description
Defines a relevant legal regulation that the business operation must comply with. Often regulations are divided into regulation articles.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Source | False | True | False | None | The source of the regulator. | False |  |
| Regulators | False | True | False | None | The regulatory authorities responsible for monitoring compliance to regulations. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Regulation Definition

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="94f61b66-333c-4827-a694-94932da307c0"></a>
# Term Name: View Data Specifications

## GUID
94f61b66-333c-4827-a694-94932da307c0

## Description
Return the data specifications, optionally filtered by the search string.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Search String | False | True | False | None | An optional search string to filter results by. | False |  |
| Output Format | False | True | False | None | Optional specification of output format for the query. | False | LIST; FORM; DICT; MD; MERMAID; REPORT |
| Starts With | False | True | False | None | If true, look for matches with the search string starting from the beginning of  a field. | False |  |
| Ends With | False | True | False | None | If true, look for matches with the search string starting from the end of  a field. | False |  |
| Ignore Case | False | True | False | None | If true, ignore the difference between upper and lower characters when matching the search string. | False |  |
| AsOfTime | False | True | False | None | An ISO-8601 string representing the time to view the state of the repository. | False |  |
| Sort Order | False | True | False | None | How to order the results. The sort order can be selected from a list of valid value. | False | ANY; CREATION_DATE_RECENT; CREATION_DATA_OLDEST; LAST_UPDATE_RECENT; LAST_UPDATE_OLDEST; PROPERTY_ASCENDING; PROPERTY_DESCENDING |
| Page Size | False | True | False | None | The number of elements returned per page. | False |  |
| Start From | False | True | False | None | When paging through results, the starting point of the results to return. | False |  |

## Qualified Name
Term::View Data Specifications

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="3e66f817-db59-4749-bd20-787df660ddf2"></a>
# Term Name: Create Data Class

## GUID
3e66f817-db59-4749-bd20-787df660ddf2

## Description
Describes the data values that may be stored in data fields. Can be used to configure quality validators and data field classifiers.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the data structure. | False |  |
| Description | False | True | False | None | A description of the data class. | False |  |
| Namespace | False | True | False | None | Optional namespace that scopes the field. | False |  |
| Match Property Names | False | True | True | None | Names of the properties that are set. | False |  |
| Match Threshold | False | True | False | None | Percent of values that must match the data class specification. | False |  |
| IsCaseSensitive | False | True | False | None | Are field values case sensitive? | False |  |
| Data Type | True | True | False | None | Data type for the data class. | False | string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other |
| Allow Duplicate Values | False | True | False | None | Allow duplicate values within the data class? | False |  |
| isNullable | False | True | False | None | Can the values within the dataclass be absent? | False |  |
| isCaseSensitive | False | True | False | None | Indicates if the values in a  data class are case sensitive. | False |  |
| Default Value | False | True | False | None | Specify a default value for the data class. | False |  |
| Average Value | False | True | False | None | Average value for the data class. | False |  |
| Value List | False | True | False | None |  | False |  |
| Value Range From | False | True | False | None | Beginning range of legal values. | False |  |
| Value Range To | False | True | False | None | End of valid range for value. | False |  |
| Sample Values | False | True | False | None | Sample values of the data class. | False |  |
| Data Patterns | False | True | False | None | prescribed format of a data field - e.g. credit card numbers. Often expressed as a regular expression. | False |  |
| In Data Dictionary | False | True | False | None | What data dictionaries is this data field in? | False |  |
| Containing Data Class | False | True | False | None | Data classes this is part of. | False |  |
| Specializes Data Class | False | True | False | None | Specializes a parent  data class. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Data Class

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="bd6f46fe-2204-439b-b866-eb0c232a6323"></a>
# Term Name: Create Governance Responsibility

## GUID
bd6f46fe-2204-439b-b866-eb0c232a6323

## Description
A responsiblity assigned to an actor or team. It could be a requirement to take a certain action in specific circumstances or to make decisions or give approvals for actions.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Supports Policies | False | True | False | None | The policies that this governance control supports. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Governance Responsibility

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="2a4d96a2-2d3e-4f81-aba9-fe41fc8e8466"></a>
# Term Name: Create Security Access Control

## GUID
2a4d96a2-2d3e-4f81-aba9-fe41fc8e8466

## Description
A technical control that defines the access control lists that an actor must belong to be entitled to perform a specific action.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Security Access Control

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="83e52f39-d352-4f97-a3df-ee39d2d9cc0e"></a>
# Term Name: Patient Height

## GUID
83e52f39-d352-4f97-a3df-ee39d2d9cc0e

## Summary
Height of patient in centimetres.

## Description
This is the height of the patient in centimetres, without shoes and to the top of the skull, ideally measured in the morning.

## Usage
Acts as a standard mechanism for measuring the height of a patient in a clinical trial.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::PatientHeight

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Clinical Trials Common Data Fields


---

<a id="aff94ae7-3934-4ff6-9949-1c31b19adf97"></a>
# Term Name: Patient Date of Birth

## GUID
aff94ae7-3934-4ff6-9949-1c31b19adf97

## Summary
Day, month and year that the patient was born.

## Description
This is the day that the person was born.  Not official birth date if different.

## Usage
Acts as a standard mechanism for measuring the age of a patient in a clinical trial.

## Qualified Name
GlossaryTerm::ClinicalTrialTerminology::PatientDateOfBirth

## Status
ACTIVE

## In Glossary
Coco Pharmaceuticals Clinical Trial Terminology

## Categories
Clinical Trials Common Data Fields


---

<a id="380b72f9-f6f3-4865-897d-bf7074b5861d"></a>
# Term Name: Create Solution Component

## GUID
380b72f9-f6f3-4865-897d-bf7074b5861d

## Description
A reusable solution component.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the solution component. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| Description | False | True | False | None | A description of the data structure. | False |  |
| Solution Component Type | False | True | False | None | Type of solution component. | False |  |
| Planned Deployed Implementation Type | False | True | False | None | The planned implementation type for deployment. | False |  |
| Initial Status | False | True | False | None | Optional lifecycle status. If not specified, set to ACTIVE. If set to Other then the value in User Defined Status will be used. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE; DISABLED; DEPRECATED; OTHER |
| In Solution Components | False | True | False | None | Solution components that include this one. | False |  |
| In Solution Blueprints | False | True | False | None | Solution Blueprints that contain this component. | False |  |
| In Information Supply Chains | False | True | False | None | The Information Supply Chains that this component is a member of. | False |  |
| Actors | False | True | False | None | Actors associated with this component. | False |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |
| Merge Update | False | True | False | None | If true, only those attributes specified in the update will be updated; If false, any attributes not provided during the update will be set to None. | False |  |

## Qualified Name
Term::Create Solution Component

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="58933d73-7f04-4899-99ce-bbd25826041a"></a>
# Term Name: Sustainability

## GUID
58933d73-7f04-4899-99ce-bbd25826041a

## Summary
A means of operating that makes effective use of replaceable resources.

## Description
In the broadest sense, sustainability refers to the ability to maintain or support a process continuously over time. In business and policy contexts, sustainability seeks to prevent the depletion of natural or physical resources, so that they will remain available for the long term.

## Qualified Name
GlossaryTerm:Sustainability

## Status
ACTIVE

## In Glossary
Sustainability Glossary


---

<a id="96598a1f-21a7-4c87-a71e-b43ec8056495"></a>
# Term Name: Create Data Field

## GUID
96598a1f-21a7-4c87-a71e-b43ec8056495

## Description
A data field is a fundamental building block for a data structure.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the Data Field | False |  |
| Description | False | True | False | None | A description of the Data Field | False |  |
| Data Type | True | True | False | None | The data type of the data field. Point to data type valid value list if exists. | False | string; int; long; date; boolean; char; byte; float; double; biginteger; bigdecimal; array<string>; array<int>; map<string,string>; map<string, boolean>; map<string, int>; map<string, long>; map<string,double>; map<string, date> map<string, object>; short; map<string, array<string>>; other |
| Position | False | True | False | None | Position of the data field in the data structure. If 0, position is irrelevant. | False |  |
| Minimum Cardinality | False | True | False | None | The minimum cardinality for a data element. | False |  |
| Maximum Cardinality | False | True | False | None | The maximum cardinality for a data element. | False |  |
| In Data Structure | False | True | False | None | The data structure this field is a member of. If display name is not unique, use qualified name. | False |  |
| Data Class | False | True | False | None | The data class that values of this data field conform to. | False |  |
| Glossary Term | False | True | False | None | Term that provides meaning to this field. | False |  |
| isNullable | False | True | False | None | Can the values within the dataclass be absent? | False |  |
| Minimum Length | False | True | False | None |  | False |  |
| Length | False | True | False | None | The length of a value for a field. | False |  |
| Precision | False | True | False | None | The precision of a numeric | False |  |
| Ordered Values | False | True | False | None | is this field in an ordered list? | False |  |
| Units | False | True | False | None | An optional string indicating the units of the field. | False |  |
| Default Value | False | True | False | None | Specify a default value for the data class. | False |  |
| Version Identifier | False | True | False | None | A user supplied version identifier. | False |  |
| In Data Dictionary | False | True | False | None | What data dictionaries is this data field in? | False |  |
| Parent Data Field | False | True | False | None | Optional parent field if this is a nested field. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Data Field

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="75712a3f-290d-4aa6-ac60-2af4150246a5"></a>
# Term Name: Create Security Group

## GUID
75712a3f-290d-4aa6-ac60-2af4150246a5

## Description
A group of actors that need to be given the same access to a specific set of resources.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Distinguished Name | False | True | False | None | Unique identity of an actor. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implementation Description | False | True | False | None | Describes how this governance control is implemnted. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Security Group

## Status
DRAFT

## In Glossary
Egeria-Markdown


---

<a id="4ae0c7c3-ae76-431c-8c64-97aa3140efc7"></a>
# Term Name: Create Threat Definition

## GUID
4ae0c7c3-ae76-431c-8c64-97aa3140efc7

## Description
The Threat entity describes a particular threat to the organization''s operations that must either be guarded against or accommodated to reduce its impact.

## Usage
| Attribute Name | Input Required | Read Only | Generated | Default Value | Notes | Unique Values | Valid Values |
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Display Name | True | True | False | None | Name of the  definition. | False |  |
| Summary | False | True | False | None | Summary of the definition. | False |  |
| Description | False | True | False | None | Description of the contents of the definition. | False |  |
| Domain Identifier | False | True | False | None | Integer representing the governance domain. All domains is 0. | False |  |
| Document Identifier | False | True | False | None | A user supplied identifier for the governance document. | False |  |
| Version Identifier | False | True | False | None | Published  version identifier. | False |  |
| Scope | False | True | False | None | Scope of the definition. | False |  |
| Importance | False | True | False | None | Importance of the definition. | False |  |
| Implications | False | True | False | None | List of implications. | False |  |
| Outcomes | False | True | False | None | List of desired outcomes. | False |  |
| Results | False | True | False | None | A list of expected results. | False |  |
| Status | False | True | False | None | The status of the agreement. There is a list of valid values that this conforms to. | False | DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE''; DEPRECATED; OTHER |
| User Defined Status | False | True | False | None | Only valid if Product Status is set to OTHER. User defined & managed status values. | False |  |
| Qualified Name | False | True | True | None | A unique qualified name for the element. Generated using the qualified name pattern  if not user specified. | True |  |
| GUID | False | False | True | None | A system generated unique identifier. | True |  |

## Qualified Name
Term::Create Threat Definition

## Status
DRAFT

## In Glossary
Egeria-Markdown


# Provenance

* Results from processing file generated_help_report.md on 2025-07-21 10:52
