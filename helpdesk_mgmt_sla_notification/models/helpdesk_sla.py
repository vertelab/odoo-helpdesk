#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
import logging

class CalanderEventsManager(models.AbstractModel):
    _inherit = 'calendar.alarm_manager'
    
    @api.model
    def _send_reminder_ticket(self,cron=False):
        logging.warning(f"{self.env.context=}")
        # Executed via cron
        logging.warning("_send_reminder_ticket _send_reminder_ticket _send_reminder_ticket _send_reminder_ticket")
        logging.warning(f"{cron}")
        tickets_by_alarm = self._get_tickets_by_alarm_to_notify('email')
        logging.warning(f"{tickets_by_alarm=}")
        raise Exception(f"{tickets_by_alarm=}")
        if not tickets_by_alarm:
            return
        logging.warning(f"{tickets_by_alarm=}")
        raise Exception(f"{tickets_by_alarm=}")
        event_ids = list(set(event_id for event_ids in tickets_by_alarm.values() for event_id in event_ids))
        logging.warning(f"{event_ids=}")
        events = self.env['calendar.event'].browse(event_ids)
        
    
    
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
               AND "ticket"."sla_deadline" - CAST("alarm"."duration" || ' ' || "alarm"."interval" AS Interval) >= %s
               AND "ticket"."sla_deadline" - CAST("alarm"."duration" || ' ' || "alarm"."interval" AS Interval) < now() at time zone 'utc'
             )''', [alarm_type, lastcall])

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


