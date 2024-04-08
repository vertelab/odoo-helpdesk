import logging

from odoo import _, api,models


_logger = logging.getLogger(__name__)

class HelpdeskMailAlias(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_route(self, message, message_dict, 
                      model=None, thread_id=None, 
                      custom_values=None):
        _logger.warning("[HELPDESK investigation] message_route"*20)

        _logger.warning(f"Incoming message subject: {message_dict['subject']}")
        _logger.warning(f"Incoming message sender: {message_dict['email_from']}")
        _logger.warning(f"Incoming message recipient: {message_dict['to']}")
        _logger.warning(f"Incoming message ID: {message_dict['message_id']}")
        _logger.warning(f"In Reply To : {message_dict['in_reply_to']}")
        _logger.warning('Routing email message with subject %s to model %s, thread ID %s', message_dict.get('subject'), model, thread_id)
        res = super(HelpdeskMailAlias, self).message_route(
            message,
            message_dict,
            model=model,
            thread_id=thread_id,
            custom_values=custom_values,
        )
        _logger.warning(f"message_route result: {res}")
        return res

    @api.model
    def _message_route_process(self, message, message_dict, routes):

        _logger.warning("[HELPDESK investigation] _message_route_process" * 20)
        _logger.warning(f"Message details: {message}")
        _logger.warning(f"Message dictionary: {message_dict}")
        _logger.warning(f"Routes: {routes}")

        res = super(HelpdeskMailAlias, self)._message_route_process(
            message,
            message_dict,
            routes
        )
        _logger.warning(f"message_route_process result: {res}")
        return res
    
    # @api.model
    # def message_process(self, model, message, custom_values=None,
    #                     save_original=False, strip_attachments=False,
    #                     thread_id=None):
    #     _logger.warning("[HELPDESK investigation] message_process" * 20)
    #     _logger.warning(f"model: {model}")
    #     _logger.warning(f"custom_values: {custom_values}")
    #     _logger.warning(f"save_original: {save_original}")
    #     _logger.warning(f"strip_attachments: {strip_attachments}")
    #     _logger.warning(f"thread_id: {thread_id}")

    #     res = super(HelpdeskMailAlias, self).message_process(
    #         model=model,
    #         message=message,
    #         custom_values=custom_values,
    #         save_original=save_original,
    #         strip_attachments=strip_attachments,
    #         thread_id=thread_id,
    #     )

    #     _logger.warning(f"message_process result: {res}")
    #     return res

    
    @api.model
    def message_new(self, msg_dict, custom_values=None):

        _logger.warning("[HELPDESK investigation] message_new" * 20)
        _logger.warning(f"Incoming message details: {msg_dict}")
        _logger.warning(f"Custom values: {custom_values}")

        res = super(HelpdeskMailAlias, self).message_new(
            msg_dict, 
            custom_values
        )

        _logger.warning(f"message_new result {res}")
        return res
    
