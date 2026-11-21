# -*- coding: utf-8 -*-
"""Helpdesk-verktyg — affärslogik för ärendehantering.

Mönstret är project_ai:s `project_ai.py`: verktygen i XML är tunna
skal som anropar metoder här. Logiken ligger i modellen, inte i
sandbox-koden — den blir testbar och läsbar.

Alla metoder är `@api.model` och anropar `_capture_session_from_ticket`
så att sessionen får domänkontext (samma väg som project_ai:s
`_capture_session_from_task`).
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class HelpdeskAI(models.AbstractModel):
    _name = 'helpdesk.ai'
    _description = 'Helpdesk AI — business logic for the ticket tools'

    # ── Kontext ────────────────────────────────────────────────────────

    @api.model
    def _capture_session_from_ticket(self, ticket_id):
        """Tagga den aktuella sessionen med ärende/kund-kontext.

        Sessionen hämtas ur env-kontexten (`_ai_context_model`/
        `_ai_context_id`, satta av openai_api-vägen). Tyst no-op om ingen
        session är aktiv — hooks får aldrig kasta.
        """
        try:
            if self.env.context.get('_ai_context_model') != \
                    'ai.coworker.session':
                return self.env['ai.coworker.session']
            sess = self.env['ai.coworker.session'].browse(
                int(self.env.context.get('_ai_context_id') or 0))
            if not sess.exists():
                return self.env['ai.coworker.session']
            sess._capture_context(ticket=ticket_id)
            return sess
        except Exception as e:
            _logger.warning('session capture from ticket failed: %s', e)
            return self.env['ai.coworker.session']

    # ── Läsning ────────────────────────────────────────────────────────

    @api.model
    def ticket_get(self, ticket_id):
        """Returnera ärendeinfo (dict) för ett helpdesk.ticket."""
        ticket = self.env['helpdesk.ticket'].sudo().browse(int(ticket_id))
        if not ticket.exists():
            return {'error': 'Ticket %s not found' % ticket_id}
        self._capture_session_from_ticket(ticket.id)
        return {
            'id': ticket.id,
            'number': ticket.number,
            'name': ticket.name,
            'partner_id': ticket.partner_id.id if ticket.partner_id else None,
            'partner_name': ticket.partner_id.name if ticket.partner_id else '',
            'stage': ticket.stage_id.name if ticket.stage_id else '',
            'team': ticket.team_id.name if 'team_id' in ticket._fields
                    and ticket.team_id else '',
            'user_id': ticket.user_id.id if 'user_id' in ticket._fields
                       and ticket.user_id else None,
            'user_name': ticket.user_id.name if 'user_id' in ticket._fields
                         and ticket.user_id else '',
            'priority': ticket.priority,
            'create_date': ticket.create_date.isoformat()
                           if ticket.create_date else None,
            'description': (ticket.description or '')[:500],
        }

    # ── Skrivning ──────────────────────────────────────────────────────

    @api.model
    def ticket_set_stage(self, ticket_id, stage):
        """Flytta ärendet till en etapp. Returnerar (ok, meddelande).

        Etappen slås upp i ärendets team (helpdesk_mgmt har `stage_id` på
        `helpdesk.ticket` och `stage_ids` på teamet). Saknas team
        används första bästa etapp med matchande namn.
        """
        ticket = self.env['helpdesk.ticket'].sudo().browse(int(ticket_id))
        if not ticket.exists():
            return False, 'Ticket %s not found' % ticket_id
        wanted = str(stage or '').strip().lower()
        if not wanted:
            return False, 'Missing stage name'
        domain = [('name', '=ilike', wanted)]
        if 'team_id' in ticket._fields and ticket.team_id:
            domain = ['|', ('team_ids', 'in', ticket.team_id.id)] + domain
        found = self.env['helpdesk.ticket.stage'].sudo().search(
            domain, limit=1)
        if not found:
            found = self.env['helpdesk.ticket.stage'].sudo().search(
                [('name', '=ilike', wanted)], limit=1)
        if not found:
            return False, 'No stage named %r' % stage
        ticket.write({'stage_id': found.id})
        self._capture_session_from_ticket(ticket.id)
        return True, 'Ticket %s moved to stage %s' % (
            ticket.number or ticket.name, found.name)

    @api.model
    def ticket_update_fields(self, ticket_id, name=None, priority=None,
                             description=None):
        """Uppdatera namn, prioritet och/eller beskrivning."""
        ticket = self.env['helpdesk.ticket'].sudo().browse(int(ticket_id))
        if not ticket.exists():
            return False, 'Ticket %s not found' % ticket_id
        vals = {}
        if name is not None and str(name).strip():
            vals['name'] = str(name).strip()
        if priority is not None and str(priority).strip():
            vals['priority'] = str(priority).strip()
        if description is not None:
            vals['description'] = str(description)
        if not vals:
            return False, 'Nothing to update'
        ticket.write(vals)
        self._capture_session_from_ticket(ticket.id)
        return True, 'Ticket %s updated: %s' % (
            ticket.number or ticket.name, ', '.join(sorted(vals)))

    @api.model
    def ticket_add_message(self, ticket_id, body):
        """Posta ett meddelande i ärendets chatter."""
        ticket = self.env['helpdesk.ticket'].sudo().browse(int(ticket_id))
        if not ticket.exists():
            return False, 'Ticket %s not found' % ticket_id
        if not body or not str(body).strip():
            return False, 'Missing message body'
        ticket.message_post(body=str(body), message_type='comment')
        self._capture_session_from_ticket(ticket.id)
        return True, 'Message posted on %s' % (
            ticket.number or ticket.name)
