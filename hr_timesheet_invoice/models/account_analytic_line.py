from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # override ondelete='cascade' => 'set null' for some case by using compute function
    move_id = fields.Many2one('account.move.line', string='Journal Item', ondelete='set null', index=True)
    allow_invoice = fields.Boolean('Allow Timesheet Invoicing', compute='_compute_allow_invoice', inverse='_inverse_allow_invoice', store=True)
    check_move_id = fields.Boolean(compute='_compute_check_move_id')
    
    @api.depends('move_id')
    def _compute_check_move_id(self):
        # replace cascade process with more flexible approach
        for record in self:
            if not record.move_id:
                if not record.employee_id:
                    record.unlink()

    @api.depends('project_id')
    def _compute_allow_invoice(self):
        for record in self:
            allow_invoice = False
            if record.project_id and record.project_id.allow_invoice:
                allow_invoice = True
            record.allow_invoice = allow_invoice

    def _inverse_allow_invoice(self):
        return True