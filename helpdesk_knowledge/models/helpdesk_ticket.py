from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    document_id = fields.many2one(comodel_name='document.page')
    post_id = fields.many2one(comodel_name="forum.post')
