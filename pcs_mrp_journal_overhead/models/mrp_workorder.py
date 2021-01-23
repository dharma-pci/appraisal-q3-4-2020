# import lib python
from datetime import datetime

# import odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# imports from odoo modules
from odoo.tools.profiler import profile


class MrpWorkorder(models.Model):
    """ inherit model mrp.workorder """

    _inherit = 'mrp.workorder'

    # Fields declaration
    overhead_duration = fields.Float(string="Overhead Duration", digits='Overhead Duration')
    journal_entries = fields.Many2one('account.move', string='Journal Entries Overhead')

    # @profile
    def record_production(self):
        # inherit function base to create journal onverhead
        if self.overhead_duration <= 0:
            raise ValidationError(_("Not allowed the value of Overhead Duration 0."))

        # create journal overhead
        journal_overhead = self.generate_journal_overhead()
        self.journal_entries = journal_overhead.id

        res = super(MrpWorkorder,self).record_production()

        return res

    @profile
    def generate_journal_overhead(self):
        # generate journal entries for Overhead
        # return record account move
        
        if not self.workcenter_id.overhead_account:
        	raise ValidationError(_("Please define first account overhead in workcenter :%s") %(self.workcenter_id.name))

        journal_stock_id = self.product_id.categ_id.property_stock_journal.id
        overhead_account_id = self.workcenter_id.overhead_account.id
        wip_account = self.env.ref('pcs_mrp_journal_overhead.account_wip')

        val_amount_overhead = self.overhead_duration * self.workcenter_id.costs_hour
        list_line=[]

        # create credit line
        vals_line_credit = {
                'account_id': overhead_account_id,
                'name': 'Overhead Amount',
                'debit': 0,
                'credit': val_amount_overhead,
            }
        list_line.append((0, 0, vals_line_credit))
            
        # create debit line
        vals_line_debit = {
                'account_id': wip_account.id,
                'name': 'WIP (Work In Progress)',
                'debit': val_amount_overhead,
                'credit': 0,
            }
        list_line.append((0, 0, vals_line_debit))

        init_acc_move = {
            'ref': self.production_id.name+" - Overhead",
            'journal_id': journal_stock_id,
            'date': datetime.today(),
            'company_id': self.env.user.company_id.id,
            'line_ids': list_line,
        }

        record_move = self.env['account.move'].create(init_acc_move)
        record_move.post()

        return record_move


