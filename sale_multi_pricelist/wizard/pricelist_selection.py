''' pricelist.selection '''
from odoo import fields, models


class PricelistSelection(models.TransientModel):
    ''' new transient model pricelist.selection '''

    _name = 'pricelist.selection'
    _description = 'Pricelist Selection'

    sale_line_id = fields.Many2one(
        'sale.order.line')
    line_ids = fields.One2many(
        'pricelist.selection.line',
        'pricelist_selected_id')
    pricelist_id = fields.Many2one('product.pricelist')

    def action_save(self):
        ''' apply pricelist to sale order line '''

        if self.pricelist_id:
            self.sale_line_id.pricelist_id = self.pricelist_id.id
            self.sale_line_id.pricelist_change()


class PricelistSelectionLine(models.TransientModel):
    ''' new transient model pricelist.selection.line '''

    _name = 'pricelist.selection.line'
    _description = 'Pricelist Selection Line'

    pricelist_selected_id = fields.Many2one(
        'pricelist.selection')
    pricelist_id = fields.Many2one(
        'product.pricelist')

    def action_apply(self):
        ''' apply selected pricelist '''

        if self.pricelist_id and self.pricelist_selected_id.sale_line_id:
            sale_line_id = self.pricelist_selected_id.sale_line_id
            self.pricelist_selected_id.pricelist_id = self.pricelist_id.id
            self.pricelist_selected_id.sale_line_id.pricelist_id = self.pricelist_id.id
            sale_line_id.pricelist_change()

