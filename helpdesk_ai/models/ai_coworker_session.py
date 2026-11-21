# -*- coding: utf-8 -*-
"""Kostnadskontext på ai.coworker.session — domänfält för helpdesk.

`helpdesk_ai`: `ticket_id` läggs via arv i bryggan (core förblir
domän-rent). `partner_id`/`pi_session_id`/`cost_context_confirmed` ligger
i ai_agent_core (res.partner = basmodul).

Registrerar även resolver-strategin "helpdesk_partner" i core-registret så
coworkers med `cost_context_partner_strategy = "helpdesk_partner"` får
partnern härledd via ärende → kund.

Mönstret är project_ai:s (`project_ai/models/ai_coworker_session.py`) —
samma hooks, samma självständighet, samma "senast arbetad kontext vinner".

MODUL: OCA `helpdesk_mgmt`, inte EE `helpdesk`. `helpdesk.ticket` har
`number`, `partner_id`, `partner_email`, `partner_name`, `stage_id`.

KÄND FÄLLA (user-mail-ai-rules design.md rad 230): OCA `helpdesk_mgmt`
sätter `partner_email`/`partner_name` via `@api.onchange`, vilket ett
programmatiskt `create()` hoppar över. Bryggan förutsätter inte att de
sätts automatiskt.
"""

import logging
import re

from odoo import fields, models

_logger = logging.getLogger(__name__)


def _helpdesk_partner_strategy(session):
    """Resolver: hitta res.partner via ärende → kund.

    Ingen gissning: saknas ärende sätts ingen partner. En påhittad kund i
    kostnadskontexten är värre än ingen kund.
    """
    if session.ticket_id and session.ticket_id.partner_id:
        session.partner_id = session.ticket_id.partner_id.id


try:
    from odoo.addons.ai_agent_core.models.ai_session import (
        register_cost_context_strategy)
    register_cost_context_strategy(
        'helpdesk_partner', _helpdesk_partner_strategy)
except Exception as e:  # pragma: no cover — modulordning
    _logger.warning('kunde inte registrera helpdesk_partner-strategi: %s', e)


class AICoworkerSessionHelpdesk(models.Model):
    _inherit = 'ai.coworker.session'

    ticket_id = fields.Many2one(
        'helpdesk.ticket', string='Ärende', index=True,
        ondelete='set null',
        help='Ärende (helpdesk.ticket) som sessionen arbetar med. '
             'Kund härleds via ärendet.')

    def _capture_context(self, ticket=None, partner=None, object_ref=None,
                         **kwargs):
        """En enda skrivpunkt för helpdesk-kostnadskontext.

        Härledning: ticket_id ← ticket; partner_id ← ticket.partner_id.
        Befintliga värden behålls om inget nytt ges ("senast arbetad
        kontext vinner" — inga nollställningar). En redan satt partner
        skrivs inte över av ärendets kund (samma regel som sale_ai fick
        efter testfyndet 2026-11-20).

        Anropar super() så övriga bryggor (project_ai, prd_ai, sale_ai)
        samlas i MRO-kedjan.
        """
        self.ensure_one()
        vals = {}
        if ticket:
            t = ticket if isinstance(ticket, models.BaseModel) else \
                self.env['helpdesk.ticket'].browse(int(ticket))
            if t:
                vals['ticket_id'] = t.id
                if t.partner_id and not self.partner_id:
                    vals['partner_id'] = t.partner_id.id
        if partner:
            par = partner if isinstance(partner, models.BaseModel) else \
                self.env['res.partner'].browse(int(partner))
            if par:
                vals['partner_id'] = par.id
        if vals:
            self.write(vals)
        return super()._capture_context(object_ref=object_ref)

    def _session_capture_context(self):
        """Core-hook: härled partner via resolver-strategin (helpdesk_ai).

        Självständig (anropar strategin direkt) så den fungerar även om
        coworkerns `cost_context_partner_strategy` inte satts än.
        """
        self.ensure_one()
        try:
            _helpdesk_partner_strategy(self)
        except Exception as e:
            _logger.warning('session capture (helpdesk) failed: %s', e)
        return super()._session_capture_context()

    def _session_auto_capture(self, prompt):
        """Deterministisk kontextfångst ur användarens prompt.

        - `ärende <id>` / `ticket <id>` / `#<id>` → ärende via numeriskt id
        - `HD<nummer>` → ärende via `number`-fältet

        Fångar bara när ärende saknas ('senast arbetad kontext vinner').
        Tyst no-op vid fel — hooks får aldrig kasta. Anropar super() så
        övriga bryggor också fångas.
        """
        self.ensure_one()
        try:
            text = (prompt or '').strip()
            if not text:
                return super()._session_auto_capture(prompt)
            if not self.ticket_id:
                # Numeriskt id: "ärende 42" / "ticket #42"
                m = re.search(
                    r'(?:ärende|arende|ticket)\s*#?\s*(\d+)', text, re.I)
                if m:
                    t = self.env['helpdesk.ticket'].browse(int(m.group(1)))
                    if t.exists():
                        self._capture_context(ticket=t)
                        return super()._session_auto_capture(prompt)
                # Ärendenummer: HD-00042 / HD42
                m = re.search(r'\bHD\s*[-/]?\s*(\d{2,})\b', text, re.I)
                if m:
                    t = self.env['helpdesk.ticket'].search(
                        [('number', 'ilike', m.group(1))], limit=1)
                    if t.exists():
                        self._capture_context(ticket=t)
                        return super()._session_auto_capture(prompt)
        except Exception as e:
            _logger.warning('session auto-capture (helpdesk) failed: %s', e)
        return super()._session_auto_capture(prompt)
