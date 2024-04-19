from odoo import api, fields, models


class Alarm(models.Model):
    _inherit = 'calendar.alarm'

    mail_template_id = fields.Many2one(
        'mail.template', string="Email Template",
        domain=[('model', 'in', ['calendar.attendee', 'helpdesk.ticket'])],
        compute='_compute_mail_template_id', readonly=False, store=True,
        help="Template used to render mail reminder content.")
