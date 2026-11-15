# odoo-helpdesk — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **6** |
| Grenar i repot | `14.0`, `16.0`, `17.0`, `18.0`, `20.0`, `main` |

## Moduler

- `helpdesk_ai`
- `helpdesk_duplicate_portal_contact`
- `helpdesk_escalation`
- `helpdesk_hierarchy_category`
- `helpdesk_mgmt_translation`
- `helpdesk_related_ticket`

## Blockerare

✅ Inga externa beroenden saknas i Odoo 19-kärnan eller OCA 19.0.

Modulerna kan troligen portas utan att vänta på externa bidrag.

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
