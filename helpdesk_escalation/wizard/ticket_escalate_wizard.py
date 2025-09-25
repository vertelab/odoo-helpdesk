import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class TicketEscalateWizard(models.TransientModel):
    _name = 'ticket.escalate.wizard'
    _description = 'This wizard lets a user escalate or change which team should handle the current ticket, regardless of their permissions.'

    ticket_id = fields.Many2one(comodel_name="helpdesk.ticket")
    ticket_team_id = fields.Many2one(comodel_name="helpdesk.ticket.team")

    def escalate(self):
        self.ticket_id.sudo().write({"team_id": self.ticket_team_id.id}) 

        action = self.env.ref("helpdesk_mgmt.helpdesk_ticket_dashboard_action")
        action = action.sudo().read()[0]

        return action 
