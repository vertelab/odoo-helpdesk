#    Copyright (C) 2020 GARCO Consulting <www.garcoconsulting.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HelpdeskSla(models.Model):
    _inherit = "helpdesk.sla"
    alarm_ids = fields.Many2many(
        'calendar.alarm', 'helpdesk_alarm_rel',
        string='Reminders', ondelete="restrict",
        help="Notifications sent to all team member to warn about SLA.")

    def _setup_alarms(self):
        """ Schedule cron triggers for future events """
        cron = self.env.ref('calendar.ir_cron_scheduler_alarm').sudo()
        alarm_types = self._get_trigger_alarm_types()
        events_to_notify = self.env['calendar.event']

        for event in self:
            for alarm in (alarm for alarm in event.alarm_ids if alarm.alarm_type in alarm_types):
                at = event.start - timedelta(minutes=alarm.duration_minutes)
                if not cron.lastcall or at > cron.lastcall:
                    # Don't trigger for past alarms, they would be skipped by design
                    cron._trigger(at=at)
            if any(alarm.alarm_type == 'notification' for alarm in event.alarm_ids):
                # filter events before notifying attendees through calendar_alarm_manager
                events_to_notify |= event.filtered(lambda ev: ev.alarm_ids and ev.stop >= fields.Datetime.now())
        if events_to_notify:
            self.env['calendar.alarm_manager']._notify_next_alarm(events_to_notify.partner_ids.ids)

