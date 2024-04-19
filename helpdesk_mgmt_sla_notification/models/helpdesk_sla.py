#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import logging


class CalendarEventsManager(models.AbstractModel):
    _inherit = 'calendar.alarm_manager'

    @api.model
    def _send_reminder_ticket(self):
        # Executed via cron
        tickets_by_alarm = self._get_tickets_by_alarm_to_notify('email')
        logging.warning(f"{tickets_by_alarm=}")
        if not tickets_by_alarm:
            return

        helpdesk_ticket_ids = list(
            set(ticket_id for ticket_ids in tickets_by_alarm.values() for ticket_id in ticket_ids)
        )
        tickets = self.env['helpdesk.ticket'].browse(helpdesk_ticket_ids)
        team_members = tickets.team_id.user_ids.mapped('partner_id')
        alarms = self.env['calendar.alarm'].browse(tickets_by_alarm.keys())
        for alarm in alarms:
            alarm_members = team_members.filtered(lambda attendee: attendee.event_id.id in tickets_by_alarm[alarm.id])
            logging.warning(f"alarm_members {alarm_members=}")
            # alarm_members.with_context(
            #     mail_notify_force_send=True,
            #     calendar_template_ignore_recurrence=True
            # )._send_mail_to_attendees(
            #     alarm.mail_template_id,
            #     force_send=True
            # )

    def _get_tickets_by_alarm_to_notify(self, alarm_type):
        """
        Get the tickets with an alarm of the given type between the cron
        last call and now.

        Please note that all new reminders created since the cron last
        call with an alarm prior to the cron last call are skipped by
        design. The attendees receive an invitation for any new ticket
        already.
        """
        lastcall = self.env.context.get('lastcall', False) or fields.date.today() - relativedelta(weeks=1)

        self.env.cr.execute('''
            SELECT "alarm"."id", "ticket"."id"
              FROM "helpdesk_ticket" AS "ticket"
              JOIN "ticket_alarm_rel" AS "ticket_alarm_rel"
                ON "ticket"."id" = "ticket_alarm_rel"."helpdesk_ticket_id"
              JOIN "calendar_alarm" AS "alarm"
                ON "ticket_alarm_rel"."calendar_alarm_id" = "alarm"."id"
             WHERE (
                   "alarm"."alarm_type" = %s
               AND "ticket"."active"
             )''', [alarm_type])

        tickets_by_alarm = {}

        for ticket in self.env['helpdesk.ticket'].search([]):
            logging.warning(f"{ticket.sla_deadline}")

        for alarm_id, tickets_id in self.env.cr.fetchall():
            logging.warning(f"{alarm_id=} {tickets_id=}")
            tickets_by_alarm.setdefault(alarm_id, list()).append(tickets_id)
        return tickets_by_alarm


class HelpdeskSla(models.Model):
    _inherit = "helpdesk.sla"

    alarm_ids = fields.Many2many(
        'calendar.alarm', 'helpdesk_alarm_rel',
        string='Reminders', ondelete="restrict",
        help="Notifications sent to all team member to warn about SLA.")
