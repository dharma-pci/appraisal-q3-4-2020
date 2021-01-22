from odoo import fields, models, _
from odoo.exceptions import UserError


class StockRule(models.Model):
    """ inherit model stock rule """
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        """ inherit function _get_stock_move_value for adding new field """
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        res.update({
            'owner_id': values.get('owner_id', False)
        })
        return res