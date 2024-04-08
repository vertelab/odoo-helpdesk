import base64
import logging

import werkzeug

import odoo.http as http
from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController

from odoo.http import request
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class HelpdeskTicketControllerExt(HelpdeskTicketController):

    def _get_teams(self):
        return (
            http.request.env["helpdesk.ticket.team"]
            .sudo()
            .with_company(request.env.company.id)
            .search([("active", "=", True), ("show_in_portal", "=", True)])
            if http.request.env.user.company_id.helpdesk_mgmt_portal_select_team
            else False
        )

    def _get_related_tickets(self):
        ticket_ids = http.request.env["helpdesk.ticket"].sudo().search([
            ('user_id', '=', http.request.env.user.id)
        ])
        return ticket_ids

    def _prepare_submit_ticket_vals(self, **kw):
        print(kw.get("related_ticket", False))
        category = http.request.env["helpdesk.ticket.category"].browse(
            int(kw.get("category"))
        )
        company = category.company_id or http.request.env.company
        vals = {
            "company_id": company.id,
            "category_id": category.id,
            "description": plaintext2html(kw.get("description")),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "channel_id": request.env.ref(
                "helpdesk_mgmt.helpdesk_ticket_channel_web", False
            ).id,
            "partner_id": request.env.user.partner_id.id,
            "partner_name": request.env.user.partner_id.name,
            "partner_email": request.env.user.partner_id.email,
            "user_id": request.env.user.id
        }
        if kw.get("related_ticket", False):
            vals['related_ticket_id'] = int(kw.get("related_ticket"))
        team = http.request.env["helpdesk.ticket.team"]
        if company.helpdesk_mgmt_portal_select_team and kw.get("team"):
            team = (
                http.request.env["helpdesk.ticket.team"]
                .sudo()
                .search(
                    [("id", "=", int(kw.get("team"))), ("show_in_portal", "=", True)]
                )
            )
            vals["team_id"] = team.id
        # Need to set stage_id so that the _track_template() method is called
        # and the mail is sent automatically if applicable
        vals["stage_id"] = team._get_applicable_stages()[:1].id
        return vals

    @http.route("/new/ticket", type="http", auth="user", website=True)
    def create_new_ticket(self, **kw):
        company = request.env.company
        category_model = http.request.env["helpdesk.ticket.category"]
        categories = category_model.with_company(company.id).search(
            [("active", "=", True)]
        )
        email = http.request.env.user.email
        name = http.request.env.user.name
        company = request.env.company
        return http.request.render(
            "helpdesk_mgmt.portal_create_ticket",
            {
                "categories": categories,
                "teams": self._get_teams(),
                "related_ticket_ids": self._get_related_tickets(),
                "email": email,
                "name": name,
                "ticket_team_id_required": (
                    company.helpdesk_mgmt_portal_team_id_required
                ),
                "ticket_category_id_required": (
                    company.helpdesk_mgmt_portal_category_id_required
                ),
            },
        )
