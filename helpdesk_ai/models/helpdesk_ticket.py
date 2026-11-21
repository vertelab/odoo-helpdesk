# -*- coding: utf-8 -*-
"""helpdesk.ticket — AI-chatt per ärende (helpdesk_ai).

Två saker som inte hörde till verktygen:

  1. En DM-kanal per ärende, skapad LAT. Den gamla modulen skapade en
     `ai.quest` per ärende i create() — en post per ärende även för dem
     som aldrig användes. Här skapas kanalen först när någon klickar.

  2. Stäng/öppna samtalet när ärendet stängs/öppnas. Den gamla gjorde
     det i en onchange på stage_id — vilket bara kördes i formuläret,
     aldrig vid import eller automatisering. Här ligger det i write().
"""

import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    ai_channel_id = fields.Many2one(
        'discuss.channel', string='AI Chat Channel',
        ondelete='set null', copy=False,
        help='DM-kanal för samtal om ärendet. Skapas lat — först när '
             'någon öppnar chatten.')

    def _get_helpdesk_coworker(self):
        """Coworkern för ärendet — data-XML:en äger namnet."""
        self.ensure_one()
        return self.env['ai.coworker'].search(
            [('name', '=', 'Helpdesk')], limit=1)

    def _ensure_ai_channel(self):
        """Skapa (eller återanvänd) DM-kanalen för ärendet."""
        self.ensure_one()
        if self.ai_channel_id:
            return self.ai_channel_id
        coworker = self._get_helpdesk_coworker()
        if not coworker:
            _logger.warning(
                'helpdesk_ai: ingen Helpdesk-coworker — kanalen skapas '
                'utan AI-koppling (ärende %s)', self.number)
        channel = self.env['discuss.channel'].sudo().create({
            'name': '[%s] %s' % (self.number or self.id, self.name),
        })
        if coworker:
            channel.write({'ai_coworker_ids': [(4, coworker.id)]})
            try:
                channel._sync_ai_coworker_members()
            except Exception as e:
                _logger.debug('helpdesk_ai: medlemssynk hoppades över: %s', e)
        self.sudo().write({'ai_channel_id': channel.id})
        return channel

    def action_open_ai_chat(self):
        """Öppna AI-chatten för ärendet (knapp i formuläret).

        Sätter ärendets kontext på kanalen INNAN den öppnas, så coworkern
        vet vilket ärende samtalet gäller redan på första turen.
        """
        self.ensure_one()
        channel = self._ensure_ai_channel()
        channel._capture_ai_context(extra_context={
            'context_model': 'helpdesk.ticket',
            'context_res_id': self.id,
            'view_type': 'form',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'discuss.channel',
            'res_id': channel.id,
            'views': [[False, 'form']],
            'target': 'current',
            'name': _('AI: %s', self.name),
        }

    def write(self, vals):
        """Stäng/öppna AI-samtalet när ärendet stängs/öppnas."""
        res = super().write(vals)
        if 'stage_id' in vals:
            for ticket in self:
                channel = ticket.ai_channel_id
                if not channel:
                    continue
                try:
                    if ticket.closed:
                        channel.sudo().write({'active': False})
                    elif not channel.active:
                        channel.sudo().write({'active': True})
                except Exception as e:
                    _logger.warning(
                        'helpdesk_ai: kunde inte växla kanal för %s: %s',
                        ticket.number, e)
        return res
