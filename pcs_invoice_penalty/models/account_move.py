from odoo import models, fields
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_penalty_invoice_count(self):
        for invoice in self:
            invoice.update({
                'penalty_invoice_count': len(invoice.penalty_invoice_ids)
            })

    penalty_invoice_ids = fields.One2many(
        'account.move', 
        'penalty_invoice_id', 
        string="Penalty Invoices"
    )
    penalty_invoice_id = fields.Many2one(
        'account.move',
        string="Invoice Ref"
    )
    penalty_invoice_count = fields.Integer(
        string="Penalty Invoice Count",
        compute="_compute_penalty_invoice_count"
    )

    def action_view_penalty_invoice(self):
        invoices = self.mapped('penalty_invoice_ids')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state,view in action['views'] \
                    if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _prepare_invoice_values(self, invoice, company, invoice_date):
        amount_penalty = 0
        if company.penalty_type == 'percent':
            percentage = company.penalty_amount_percent
            amount_penalty = (percentage / 100) * invoice.amount_total
        else:
            amount_penalty = company.penalty_amount
            # Convert amount penalty to invoice currency if different from company currency
            if invoice.currency_id.id != company.currency_id.id:
                amount_penalty = company.currency_id._convert(amount_penalty, invoice.currency_id, \
                    company, invoice_date)
        line_vals = self._prepare_invoice_line_values(company.penalty_product_id, amount_penalty)
        return {
            'partner_id': invoice.partner_id.id,
            'type': 'out_invoice',
            'state': 'draft',
            'invoice_date': invoice_date,
            'invoice_user_id': invoice.invoice_user_id.id,
            'penalty_invoice_id': invoice.id,
            'currency_id': invoice.currency_id.id,
            'invoice_line_ids': [(0, 0, line_vals)],
        }
    
    def _prepare_invoice_line_values(self, product, amount_penalty):
        return {
            'product_id': product.id,
            'name': product.name,
            'account_id': product.categ_id.property_account_income_categ_id.id,
            'quantity': 1,
            'price_unit': amount_penalty,
            'tax_ids': False,
        }

    def cron_create_penalty_invoice(self):
        context = self.env.context
        company_obj = self.env['res.company']
        invoice_obj = self.env['account.move']

        check_date = context.get('check_date') or fields.Date.today()
        if isinstance(check_date, str):
            check_date = fields.Date.from_string(check_date)
        company_ids = company_obj.search([('penalty_type', '!=', False)])
        for company in company_ids:
            delay = int(company.penalty_due_date)

            due_date = check_date - relativedelta(days=delay + 1)
            domain = [
                ('company_id', '=', company.id),
                ('invoice_date_due', '<=', due_date),
                ('state', 'in', ['posted']),
                ('invoice_payment_state', 'not in', ['paid']),
                ('type', 'in', ['out_invoice']),
                ('penalty_invoice_ids', '=', False), # Invoice do not have penalty invoice
                ('penalty_invoice_id', '=', False), # Invoice is not a penalty invoice
            ]
            invoice_ids = invoice_obj.search(domain)
            for invoice in invoice_ids:
                vals = self._prepare_invoice_values(invoice, company, check_date)
                new_penalty_invoice = invoice_obj.create(vals)
                invoice.write({
                    'penalty_invoice_ids': [(4, new_penalty_invoice.id)]
                })

            


    