from odoo import models, fields, api, _


class HelpdeskTicketCategory(models.Model):
    _inherit = 'helpdesk.ticket.category'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'

    parent_id = fields.Many2one('helpdesk.ticket.category', string="Parent Category")
    parent_path = fields.Char(index=True, unaccent=False)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

