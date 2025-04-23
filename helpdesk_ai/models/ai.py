import re
import markdown
from markupsafe import Markup
from bs4 import BeautifulSoup
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError

import logging

_logger = logging.getLogger(__name__)



class AIQuestSession(models.Model):
    _inherit = 'ai.quest.session'

    ai_type = fields.Selection(
        selection_add=[('helpdesk-chat', 'Chat with ticket')],
        ondelete={'helpdesk-chat': 'cascade'}
    )


class AIAgent(models.Model):
    _inherit = "ai.agent"

    ai_type = fields.Selection(
        selection_add=[('helpdesk-chat', 'Chat with ticket')],
        ondelete={'helpdesk-chat': 'cascade'}
    )

    def agent_extra_context(self, quest, record=None):
        res = super().agent_extra_context(quest=quest, record=record)
        if self.ai_type == "helpdesk-chat":
            helpdesk_ticket_id = self.env['helpdesk.ticket'].search([('ai_quest_id', '=', quest.id)], limit=1)
            if helpdesk_ticket_id:
                res['Ticket Name'] = helpdesk_ticket_id.name
                res['Ticket number'] = helpdesk_ticket_id.number
                res['Assigned User'] = helpdesk_ticket_id.user_id.name
                res['Ticket Priority'] = helpdesk_ticket_id.priority
                res['Ticket Description'] = helpdesk_ticket_id.description
                res['Ticket Closed Date'] = helpdesk_ticket_id.closed_date
                res['Ticket Assigned Date'] = helpdesk_ticket_id.assigned_date
                res['Ticket Solution'] = self._ticket_solution()
        return res

    def _ticket_solution(self):
        message_comment_type = self.message_ids.filtered(lambda message: message.message_type == 'comment')
        ticket_solution = _('No Solution Provided Yet!')
        if message_comment_type:
            ticket_solution = BeautifulSoup(
                message_comment_type[0].body.encode('utf-8').decode('unicode_escape'), 'html.parser'
            ).get_text()
        return ticket_solution


class AIQuest(models.Model):
    _inherit = "ai.quest"

    ai_type = fields.Selection(
        selection_add=[('helpdesk-chat', 'Chat with ticket')],
        ondelete={'helpdesk-chat': 'cascade'}
    )

    def server_action(self, records):
        if self.init_type == 'server-action' and self.server_action_id:
            if self._check_quest_error():
                raise UserError(self._check_quest_error())
            vals = self._server_action_values(records=records)
            # res = self.run(**vals)

            for record in records:
                prompt = f"What is the solution to this helpdesk ticket: {record.number}"
                result = self.run(prompt=prompt, record=record)
                if result:
                    ai_messages = self._get_last_ai_message(result.get('result', {}).get('messages', False))
                    answer = re.sub(
                        r'<think>.*?</think>', '', markdown.markdown(ai_messages.content), flags=re.DOTALL)
                    record.with_user(SUPERUSER_ID).message_post(
                        body=Markup(answer),
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                    )


            # self.log_message(f'server-action {res}')