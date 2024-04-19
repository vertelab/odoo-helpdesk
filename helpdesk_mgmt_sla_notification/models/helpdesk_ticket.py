#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"
        
    alarm_ids = fields.Many2many(
        'calendar.alarm', 'ticket_alarm_rel',
        string='Reminders', ondelete="restrict",
        help="Notifications sent to all teammembers to remind of the SLA.", column1="helpdesk_ticket_id", column2="calendar_alarm_id")

    
