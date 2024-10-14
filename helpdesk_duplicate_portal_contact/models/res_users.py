from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Find duplicate contacts"


    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)

        if self.env['ir.config_parameter'].sudo().get_param('helpdesk.helpdesk_on_duplicate'):
            users.duplicates_create_helpdesk_ticket(users)

        return users

    def duplicates_create_helpdesk_ticket(self, users):
      for user in users:
        duplicate_partners = self.env['res.partner'].search([("email", '=ilike', user.login)])
        if len(duplicate_partners) >= 1:
            partner_links = "\n".join([f"{partner.name}\n/web#id={partner.id}&model=res.partner&view_type=form\n" for partner in duplicate_partners])
            _logger.warning(f"{partner_links=}")
            ticket = {
                "name": _(f"Duplicate contacts {user.login}"),
                "description": _("""Duplicate contacts with the same email. Please combine them.
User: %(user_login)s

Duplicate contacts:
%(partner_links)s""") % {
                    'user_login': user.login,
                    'partner_links': partner_links
                },
                "team_id": int(self.env['ir.config_parameter'].sudo().get_param('helpdesk.helpdesk_team_id')),
            }

            ticket = self.env["helpdesk.ticket"].create(ticket)
            _logger.warning(f"{ticket=}")

