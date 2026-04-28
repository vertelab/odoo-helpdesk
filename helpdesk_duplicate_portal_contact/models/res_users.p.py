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
        # #if VERSION >= "18.0"
        'view_mode': 'list,form',
        # #if VERSION <= "17.0"
        'view_mode': 'tree,form',
        'res_model': 'res.partner',
        'domain': [('id', 'in', self.duplicate_partner_ids.ids)],
        'target': 'current',
         }


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
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        for user in users:
            duplicate_partners = self.env['res.partner'].search([
                '|',("email", '=ilike', user.login),('id','=',user.partner_id.id)
            ])
            if len(duplicate_partners.filtered(lambda r: r.id != user.partner_id.id)) >= 1: ## Exclude our own partner when we see if there are duplicates since some functions set an email when we create an portal user.
                partner_links = "<br/>".join([
                    f"{partner.name}<br/>{base_url}/web#id={partner.id}&model=res.partner&view_type=form<br/>"
                    for partner in duplicate_partners
                ])
                _logger.warning(f"{partner_links=}")
                ticket = {
                    "name": _(f"Duplicate contacts {user.login}"),
                    "description": _("""Duplicate contacts with the same email. Please combine them.<br/>
User: %(user_login)s<br/><br/>
Duplicate contacts:<br/>%(partner_links)s""") % {
                        'user_login': user.login,
                        'partner_links': partner_links
                    },
                    "user_id":False,
                    "team_id": int(self.env['ir.config_parameter'].sudo().get_param('helpdesk.helpdesk_team_id')),
                }

                ticket = self.env["helpdesk.ticket"].create(ticket)
                ticket.duplicate_partner_ids = [(6, 0, duplicate_partners.ids)]
