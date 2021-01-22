from odoo import fields, models, _
from odoo.exceptions import UserError


class InvoiceActivitiesWizard(models.TransientModel):
    _name = 'invoice.activities.wizard'
    _description = 'invoice activities wizard'

    def _get_partner_ids_domain(self):
        projects = self.env['project.project'].search([])
        partners = projects.mapped('partner_id')
        return [('id', 'in', partners.ids)]

    groupby_project = fields.Boolean()
    groupby_partner = fields.Boolean()
    add_timesheet_date = fields.Boolean('Add timesheet Date in Invoice Line')
    add_timesheet_desc = fields.Boolean('Add timesheet Description in Invoice Line')

    project_ids = fields.Many2many('project.project')
    partner_ids = fields.Many2many('res.partner', domain=_get_partner_ids_domain)
    date_from = fields.Date()
    date_to = fields.Date()

    def _prepare_invoice_data(self, domain):
        rows = self.env['account.analytic.line'].search(domain)

        if not rows:
            raise UserError(_('No timesheet found for selected Filters / Options'))

        # get sales journal
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale')
        ], limit=1)
        if not journal:
            raise UserError(_('Please create sales journal first'))

        lines = []
        partner_ids = []
        for row in rows:
            partner_ids.append(row.partner_id.id)
            name = row.employee_id.name
            if self.add_timesheet_desc:
                name += '\ndescription : %s' % row.name
            if self.add_timesheet_date:
                name += '\ndate : %s' % row.date
            line = {
                'name': name,
                'account_id': journal.default_credit_account_id.id,
                'analytic_account_id': row.project_id.analytic_account_id.id,
                'analytic_line_ids': [(6, 0, row.ids)],
                'quantity': row.unit_amount,
                'price_unit': row.employee_id.timesheet_cost,
            }
            lines.append(line)
        
        partner_ids = list(set(partner_ids))
        # only 1 partner_id or nothing
        partner_id = partner_ids[0] if len(partner_ids) == 1 else False

        return {
            'type': 'out_invoice',
            'partner_id': partner_id,
            'journal_id': journal.id,
            'invoice_line_ids': lines,
        }

    def create_invoices(self):
        domain = [
            ('employee_id', '!=', False),
            ('allow_invoice', '=', True),
            ('move_id', '=', False),
        ]

        if self.project_ids:
            domain.append(['project_id', 'in', self.project_ids.ids])
        
        if self.partner_ids:
            domain.append(['partner_id', 'in', self.partner_ids.ids])

        if self.date_from > self.date_to:
            raise UserError(_('Date filter value is overlapping (date_from > date_to)'))

        if self.date_from:
            domain.append(['date', '>=', self.date_from])
        if self.date_to:
            domain.append(['date', '<=', self.date_to])
        
        datas = []
        use_groupby = self.groupby_partner or self.groupby_project
        if use_groupby:
            groupby = []
            if self.groupby_partner:
                groupby.append('partner_id')
            if self.groupby_project:
                groupby.append('project_id')
            groupping = self.env['account.analytic.line'].web_read_group(domain, ['id'], groupby, lazy=False)
        
            for group in groupping.get('groups'):
                data = self._prepare_invoice_data(group.get('__domain'))
                datas.append(data)
        else:
            data = self._prepare_invoice_data(domain)
            datas.append(data)

        if not datas:
            raise UserError(_('No invoice data found'))

        invoices = self.env['account.move'].create(datas)

        if self._context.get('open_invoices', False):
            ref = self.env.ref('account.action_move_out_invoice_type')
            action = ref.read()[0]
            action['domain'] = [
                ('type', '=', 'out_invoice'), 
                ('id', 'in', invoices.ids)
            ]
            return action
        return {'type': 'ir.actions.act_window_close'}