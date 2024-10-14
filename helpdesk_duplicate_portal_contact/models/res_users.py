from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Find duplicate contacts"

    @api.model_create_multi
    def create(self, vals_list):
        
        users = super(ResUsers,self).create(vals_list)

        if self.env['ir.config_parameter'].sudo().get_param('helpdesk.helpdesk_on_duplicate'):

            self.duplicates_create_helpdesk_ticket(users)

        return users

    def duplicates_create_helpdesk_ticket(self,users):

        for user in users:

            num_res_partner = self.env['res.partner'].search_count([("email", '=ilike', user.login)])

            if num_res_partner >= 1:

                ticket = {

                    "name": "Duplicate contacts",
                    "description": f"Duplicate contacts with the same email. Please combine them.\nUser: {user.login}",
                    "team_id": self.env['ir.config_parameter'].sudo().get_param('helpdesk.helpdesk_team_id'),
                    "company_id": user.company_id.id,
                }

                self.env["helpdesk.ticket"].create(ticket)
