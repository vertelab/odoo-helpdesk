from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ConfSetting(models.TransientModel):
    _inherit = "res.config.settings"

    helpdesk_on_duplicate = fields.Boolean(string="Duplicate Contacts", store=True, config_parameter='helpdesk.helpdesk_on_duplicate')
    helpdesk_team_id = fields.Many2one(comodel_name="helpdesk.ticket.team", string="Helpdesk Team", config_parameter='helpdesk.helpdesk_team_id')

    def set_values1(self):
        res = super(ConfSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('helpdesk.helpdesk_on_duplicate', self.helpdesk_on_duplicate)
        self.env['ir.config_parameter'].sudo().set_param('helpdesk.helpdesk_team_id', self.helpdesk_team_id)
        return res