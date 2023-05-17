from odoo import _, api, fields, models
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def create_project_task_from_ticket(self):
        
        if self.task_id : raise UserError(_("A task already exists for this ticket. Remove the assigned 'Task' to create a new task"))
        if not self.project_id: raise UserError(_("You must assign a 'Project' to the ticket in order to convert it to a task."))
        
        
        # Define models used in this function
        ProjectTask = self.env['project.task']
        MailMessage = self.env['mail.message']
        IrAttachment = self.env['ir.attachment']
        
        # Access the information from the specific helpdesk.ticket
        ticket_name = self.name
        ticket_description = self.description
        ticket_messages = reversed(self.message_ids) # Reversed in order to display the messages in the right order.
        
        # Set company_id and project_id based on the current helpdesk.ticket
        company_id = self.company_id.id
        project_id = self.project_id.id
        task_name_extra = " - " + ticket_name if ticket_name else ""
        
        # Prepare values for the new project.task
        new_task_values = {
            'name': self.number + task_name_extra,
            'description': ticket_description,
            'project_id': project_id,
            'date_deadline': False,
            'kanban_state': 'normal',
            'company_id': company_id,
            'partner_id' : self.partner_id.id,
            'user_id' : self.user_id.id,
            'priority' : "1" if self.priority == "3" else "0"
        }

        # Create a new project.task using the prepared values
        new_task = ProjectTask.create(new_task_values)
        
        # Sets the newly created task to the task-field in the ticket.
        self.task_id = new_task.id
        
        # Copy the messages from helpdesk.ticket to the newly created project.task
        for message in ticket_messages:
            new_message_values = {
                'body': message.body,
                'author_id': message.author_id.id,
                'message_type': message.message_type,
                'subtype_id': message.subtype_id.id,
                'model': 'project.task',
                'res_id': new_task.id,
                'date': message.date,
                'has_error' : message.has_error,
                # 'notification_ids' : message.notification_ids
            }
            MailMessage.create(new_message_values)
            
        # Search for attachments related to the helpdesk.ticket
        ticket_attachments = IrAttachment.search([
            ('res_model', '=', 'helpdesk.ticket'),
            ('res_id', '=', self.id)
        ])
        
        # Copy the attachments from helpdesk.ticket to the newly created project.task
        for attachment in ticket_attachments:
            new_attachment_values = {
                'name': attachment.name,
                'type': attachment.type,
                'datas': attachment.datas,
                'public': attachment.public,
                'res_model': 'project.task',
                'res_id': new_task.id,
                'mimetype': attachment.mimetype,
            }
            IrAttachment.create(new_attachment_values)

        # Posts message to newly created task with link back to original ticket
        refs = f"<a href=# data-oe-model=helpdesk.ticket data-oe-id={self.id}>{self.number}</a>"
        message = _("This task was created using the following ticket: %s") % refs
        new_task.message_post(body=message)
        
        # Posts message to newly created task with link back to original ticket
        refs = f"<a href=# data-oe-model=project.task data-oe-id={new_task.id}>{new_task.name}</a>"
        message = _("The following task has been created using this ticket: %s") % refs
        self.message_post(body=message)
        
        # Archive the current helpdesk.ticket
        self.active = False
        
        # Return an action to open the newly created task
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': new_task.id,
            'view_mode': 'form',
            'target': 'current',
        }
        return action