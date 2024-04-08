from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    related_ticket_id = fields.Many2one('helpdesk.ticket', string="Related Ticket", readonly=True)
