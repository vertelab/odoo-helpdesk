from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.TransientModel):
    _name = 'ticket.escalate.wizard'
    _description = 'This wizard lets a user escalate or change which team should handle the current ticket, regardless of their permissions.'

    ticket_id = fields.Many2one(comodel_name="helpdesk.ticket")
    ticket_team_id = fields.Many2one(comodel_name="helpdesk.ticket.team")

    def escalate(self):
        self.ticket_id.sudo().write({"team_id": self.ticket_team_id.id}) 
