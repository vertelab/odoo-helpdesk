from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    duplicate_partner_ids = fields.Many2many('res.partner', string='Duplicate Contacts')

    duplicate_partner_count = fields.Integer(string='Duplicate Contacts', compute='_compute_duplicate_partner_count')

    @api.depends('duplicate_partner_ids')
    def _compute_duplicate_partner_count(self):
        for ticket in self:
            ticket.duplicate_partner_count = len(ticket.duplicate_partner_ids)

    def action_view_duplicate_contacts(self):
        self.ensure_one()
        return {
        'name': 'Duplicate Contacts',
        'type': 'ir.actions.act_window',
        'view_mode': 'list,form',
