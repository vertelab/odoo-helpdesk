#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Ticket SLA Notifications",
    "summary": "Add SLA Notifications to the tickets for Helpdesk Management.",
    "author": "GARCO Consulting, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/helpdesk",
    "license": "AGPL-3",
    "category": "After-Sales",
    "version": "16.0.2.0.1",
    "depends": ["base", "helpdesk_mgmt_sla", "calendar"],
    "data": [
        "data/ticket_helpdesk_sla_cron.xml",
        "data/mail_template_data.xml",
        "views/helpdesk_sla_views.xml",
        "views/helpdesk_ticket.xml",
        #"views/helpdesk_ticket_team_views.xml",
    ],
}
