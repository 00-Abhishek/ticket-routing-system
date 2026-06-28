# Phase 5 Entity Analysis

## Scope

- Dataset: `data/all_tickets_processed_improved_v3.csv`
- Rows analyzed: 47,837
- Columns used: `Document`, `Topic_group`
- Goal: inspect the ticket corpus and design an entity taxonomy only.
- Extraction implementation status: not implemented in this phase.

## Class Samples

The samples below are representative snippets selected from each class. They show that the corpus is realistic but noisy: email-style greetings, dates, signatures, repeated quoted replies, and generic service-desk language are common.

### Access

- `confluence access for wednesday february pm confluence please confluence thanks`
- `password reset open access dear can you please help with rights for laptop order reset password going expire few days...`
- `confluence access thursday pm confluence hi please give confluence job engineer`

### Administrative rights

- `windows upgrade failed upgrade failed hello please raise ticket for issue below upgrade error...`
- `outlook breaks when switching to cable...`
- `outlook access on friday july pm hi wondering way personal phone calendar...`

### HR Support

- `new starter bucharest friday pm hello va date administration officer`
- `set up new service sn friday pm sn hello please find attached sn form...`
- `allocation pm allocation importance high hi please make changes allocate...`

### Hardware

- `monitor request vulcan friday october pm hello please log each user monitor allocation...`
- `stopped when docker start was executed... server was stopped when executed docker start...`
- `extra laptop for trainings october trainings importance high...`

### Internal Project

- `create new unknown pipeline unknown pipeline setup form hi please log based bellow...`
- `delete project oracle pas pm re dear please ask delete due...`
- `new project codes to be created pas thursday...`

### Miscellaneous

- `restart sent friday december restart hello can you please log incident for restart...`
- `expense report not found expense report found hello can you check why expense report here...`
- `ram allocation wednesday pm hello... requisition rejected task application...`

### Purchase

- `new delivery intend intend hello received intend headsets partial po please advise...`
- `new purchase po purchase po dear purchased galaxy tab link please log allocation...`
- `new purchase po friday july purchase po dear purchased tv supports ceiling...`

### Storage

- `mailbox problem july pm mailbox problem hello please help mailbox even entered credentials work...`
- `new shared mailbox co wednesday november pm shared mailbox hello please create shared mailbox...`
- `increase mailbox size thursday pm more hello please help by granting more...`

## Recurring Entity Evidence

### SOFTWARE

Software and application names are present and worth extracting. The strongest observed terms are:

| Term | Ticket Count | Dominant Classes |
| --- | ---: | --- |
| Oracle | 3,948 | HR Support, Miscellaneous, Internal Project |
| Application | 1,802 | Hardware, Miscellaneous, HR Support |
| Confluence | 1,542 | Access |
| Software | 1,400 | Hardware, Administrative rights, Access |
| Teams | 820 | Hardware, Miscellaneous, HR Support |
| Windows | 759 | Administrative rights, Hardware |
| Outlook | 653 | Administrative rights, Storage, Hardware |
| Excel | 428 | Hardware, HR Support, Access |
| Visual Studio | 299 | Access |
| Chrome | 262 | Hardware |
| Active Directory | 160 | Access, Miscellaneous, Hardware |

Other low-frequency but valid candidates include Word, Edge, Java, Slack, SAP, Unix, Zoom, Acrobat, and VS Code.

### DEVICE

Device and asset mentions are strong and frequent, especially in Hardware and Purchase tickets.

| Term | Ticket Count | Dominant Classes |
| --- | ---: | --- |
| Card | 2,068 | HR Support, Access |
| Phone | 2,059 | Hardware, Purchase, HR Support |
| Mobile | 1,699 | Hardware, HR Support, Access |
| Laptop | 1,685 | Hardware |
| Monitor | 1,063 | Hardware, Purchase |
| Server | 1,058 | Hardware, Administrative rights, Access |
| Machine | 828 | Hardware, Access |
| Computer | 811 | Hardware, Miscellaneous |
| Access card | 739 | Access, HR Support |
| PC | 681 | Access, Hardware |
| Printer | 362 | Miscellaneous, Hardware, HR Support |
| Mouse | 297 | Hardware, Purchase |
| Keyboard | 265 | Hardware, Purchase |

Other valid device candidates include switch, disk, desktop, badge, workstation, scanner, headset, camera, hard drive, router, ID card, docking station, dock, and tablet.

### ERROR_CODE

Strict error-code entities are not meaningfully present in this dataset.

Regex scans found:

| Pattern Type | Matching Tickets |
| --- | ---: |
| Hex codes like `0x80070005` | 0 |
| Windows KB IDs like `KB123456` | 0 |
| HTTP status codes like `404`, `500` | 0 |
| Prefixed IDs like `ERR-123`, `INC123`, `REQ123` | 0 |
| Phrases like `error code X123` | 0 |

However, generic failure language is common:

| Signal | Matching Tickets |
| --- | ---: |
| `error` / `errors` | 4,717 |
| `failed` / `failure` / `fails` / `failing` | 1,166 |

Recommendation: keep `ERROR_CODE` in the taxonomy for future user-entered tickets and demo examples, but treat it as a low-frequency entity for this training corpus. The future extractor should use strict patterns only, not label generic phrases like `error occurred` as an `ERROR_CODE`.

### SYSTEM

System/resource names are very common and should be part of the entity design. These are often routing-relevant.

| Term | Ticket Count | Dominant Classes |
| --- | ---: | --- |
| Access | 9,194 | HR Support, Hardware, Access |
| Application | 1,802 | Hardware, Miscellaneous, HR Support |
| Account | 1,589 | Access |
| Mailbox | 1,419 | Storage, HR Support |
| Folder | 1,059 | Storage |
| Server | 1,058 | Hardware |
| Permissions | 891 | Hardware, Access, Storage |
| Storage | 797 | Storage, HR Support, Hardware |
| Backup | 564 | HR Support, Hardware |
| Network | 515 | Hardware |
| Drive | 417 | Hardware, Administrative rights, Storage |
| Database | 386 | Hardware, HR Support |
| Domain | 358 | Hardware, Access |
| Portal | 233 | Hardware, HR Support |
| Active Directory | 160 | Access, Miscellaneous, Hardware |

Other useful system terms include admin rights, payroll, ticketing, file share, and service desk.

### LOCATION

Location entities exist, but many are generic workplace references rather than city/country names.

| Term | Ticket Count | Dominant Classes |
| --- | ---: | --- |
| Floor | 2,234 | Hardware, HR Support, Access |
| Site | 1,466 | Hardware, Miscellaneous, Storage |
| Room | 661 | Hardware |
| Remote | 494 | Hardware, Access |
| Meeting room | 382 | Hardware |
| Building | 352 | Hardware, HR Support, Access |
| Branch | 49 | Miscellaneous, Hardware, Access |
| Desk | 43 | Hardware, Miscellaneous |
| Conference room | 30 | Hardware |
| Reception | 21 | Purchase, Hardware |
| Data center | 6 | Access, Hardware |
| Delhi | 2 | Purchase, Hardware |

Recommendation: extract workplace location phrases such as floor, site, building, room, meeting room, conference room, reception, branch, remote, and data center. City/country extraction should be optional because explicit geography appears sparse.

## Entity Taxonomy

| Entity | Definition | Evidence Strength | Example Values | Recommended Phase 6/NER Strategy |
| --- | --- | --- | --- | --- |
| `SOFTWARE` | Named software, applications, platforms, operating systems, or tools. | High | Oracle, Confluence, Windows, Outlook, Excel, Visual Studio, Chrome, Active Directory | Use configurable phrase patterns plus aliases. Keep generic `application` only when useful for routing context. |
| `DEVICE` | Physical hardware, endpoint assets, peripherals, or access media. | High | laptop, monitor, phone, mobile, server, printer, keyboard, access card | Use phrase patterns with singular/plural variants. Prioritize hardware and purchase routing features. |
| `SYSTEM` | Infrastructure, account, storage, permission, or business-system resources. | High | mailbox, folder, account, permissions, backup, network, drive, database, portal | Use phrase patterns and allow overlap with `SOFTWARE` for terms like Active Directory. Resolve priority in extraction rules. |
| `LOCATION` | Workplace, site, room, building, floor, or remote-work location references. | Medium | floor, site, room, meeting room, building, branch, remote, data center | Use phrase patterns. Avoid over-detecting pronouns or generic words such as `us` unless context supports location. |
| `ERROR_CODE` | Machine-readable error identifiers or coded failure references. | Low in this corpus | none found in strict scans | Keep strict regex patterns for future tickets and demos, but do not extract generic `error` text as a code. |

## Design Notes For Future Extraction

- Use spaCy `EntityRuler` or `PhraseMatcher` with a configurable pattern file.
- Prefer exact phrase matching for known software, device, system, and location terms.
- Add case-insensitive aliases, for example `pc` and `computer`, `access card` and `badge`, `data center` and `datacenter`.
- Let longer phrases win over shorter phrases, for example `access card` before `card`, `meeting room` before `room`, and `active directory` before `directory`.
- Treat ambiguous terms carefully:
  - `card` can mean access card, time card, or purchase card.
  - `server` can be a device or a system; classify as `SYSTEM` unless the surrounding text suggests physical hardware.
  - `application` is common but generic; extract only if paired with action words such as install, access, failed, or requisition.
  - `us` appears in text but is often a pronoun, not a location.
- For `ERROR_CODE`, use strict regex patterns only:
  - `0x[0-9A-Fa-f]{4,}`
  - `ERR[-_ ]?\d+`
  - `ERROR[-_ ]?\d+`
  - `HTTP 4xx/5xx` style codes
  - `KB\d+`

## Final Recommendation

The dataset supports a rule-based NER design centered on `SOFTWARE`, `DEVICE`, `SYSTEM`, and `LOCATION`. `ERROR_CODE` should remain in the project taxonomy because it is useful for IT support demos and live user tickets, but the current corpus does not contain enough strict error-code examples to treat it as a frequent dataset-derived entity.

