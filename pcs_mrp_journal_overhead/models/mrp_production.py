# import lib python
from datetime import datetime

# import odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# imports from odoo modules
from odoo.tools.profiler import profile

class MrpProduction(models.Model):
    """ inherit model mrp.production """

    _inherit = 'mrp.production'

    # Fields declaration
    journal_entries_raw_material = fields.Many2one('account.move', string='Journal Entries Raw Material')
    journal_entries_finished_goods = fields.Many2one('account.move', string='Journal Entries finished Goods')

    # @profile
    def post_inventory(self):
        # inherit function base to create journal onverhead
        res = super(MrpProduction,self).post_inventory()

        # generete journal raw material
        journal_raw_material, total_amount = self.generate_journal_raw_material()
        self.journal_entries_raw_material = journal_raw_material.id
        # generete journal finished goods
        journal_finished_goods = self.generate_journal_finished_goods(total_amount)
        self.journal_entries_finished_goods = journal_finished_goods.id

        return res
         
    @profile
    def generate_journal_raw_material(self):
        # generate journal entries for raw material
        # return record account move and total amount raw material

        raw_material_account = self.env.ref('pcs_mrp_journal_overhead.account_stock_raw_material') 
        wip_account = self.env.ref('pcs_mrp_journal_overhead.account_wip')
        journal_stock_id = self.product_id.categ_id.property_stock_journal.id

        list_line = []
        total_amount = 0

        for component in self.move_raw_ids:
            amount = component.product_id.standard_price
            total_amount += amount*component.quantity_done
            init_line_credit = {
                'account_id': raw_material_account.id,
                'name': component.product_id.name,
                'debit': 0,
                'credit': amount*component.quantity_done,
            }
            list_line.append((0, 0, init_line_credit))

        vals_line_debit = {
                'account_id': wip_account.id,
                'name': 'WIP (Work In Progress)',
                'debit': total_amount,
                'credit': 0,
            }
        list_line.append((0, 0, vals_line_debit))

        init_acc_move = {
            'ref': self.name+" - Raw Materials",
            'journal_id': journal_stock_id,
            'date': datetime.today(),
            'company_id': self.env.user.company_id.id,
            'line_ids': list_line,
        }

        record_move = self.env['account.move'].create(init_acc_move)
        record_move.post()

        return record_move, total_amount

    @profile
    def get_overhead_amount(self):
        ''' function to get overhead amount '''
        # return total amount workorder overhead

        total_amount = 0
        for workorder in self.workorder_ids:
            wip_account = self.env.ref('pcs_mrp_journal_overhead.account_wip')
            journal_line = workorder.journal_entries.line_ids.filtered(lambda x:x.account_id.id == wip_account.id)
            amount = journal_line.debit
            total_amount += amount
        return total_amount

    @profile
    def generate_journal_finished_goods(self, total_amount):
        # generate journal entries for finished goods
        # return record account move

        get_overhead_amount = self.get_overhead_amount()
        amount_finished_goods = get_overhead_amount+total_amount

        finished_goods_account = self.env.ref('pcs_mrp_journal_overhead.account_stock_finished_goods') 
        wip_account = self.env.ref('pcs_mrp_journal_overhead.account_wip')
        journal_stock_id = self.product_id.categ_id.property_stock_journal.id

        list_line=[]
            
        # create credit line
        vals_line_credit = {
                'account_id': wip_account.id,
                'name': 'WIP (Work In Progress)',
                'debit': 0,
                'credit': amount_finished_goods,
            }
        list_line.append((0, 0, vals_line_credit))


        # create debit line
        vals_line_debit = {
                'account_id': finished_goods_account.id,
                'name': self.product_id.name,
                'debit': amount_finished_goods,
                'credit': 0,
            }
        list_line.append((0, 0, vals_line_debit))

        init_acc_move = {
            'ref': self.name+" - Finished Goods",
            'journal_id': journal_stock_id,
            'date': datetime.today(),
            'company_id': self.env.user.company_id.id,
            'line_ids': list_line,
        }

        # create acount move
        record_move = self.env['account.move'].create(init_acc_move)
        record_move.post()

        return record_move





        