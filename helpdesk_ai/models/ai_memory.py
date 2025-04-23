from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from bs4 import BeautifulSoup
import logging

_logger = logging.getLogger(__name__)



class AIMemory(models.Model):
    _inherit = 'ai.memory'

    def _model_memory_type_data(self, memory):
        raw_documents = super()._model_memory_type_data(memory)
        mail_message = self.env['mail.message']
        if self.model_id.model == 'helpdesk.ticket':
            for rec in raw_documents:
                message_ids = mail_message.browse(rec.get('message_ids'))
                message_comment_type = message_ids.filtered(lambda message: message.message_type == 'comment')
                if message_comment_type:
                    ticket_solution = BeautifulSoup(
                        message_comment_type[0].body.encode('utf-8').decode('unicode_escape'), 'html.parser'
                    ).get_text()
                    rec['solution'] = ticket_solution
                else:
                    rec['solution'] = _('No Solution Provided')
        return raw_documents




