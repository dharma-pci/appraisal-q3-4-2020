from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields
# 
class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        ''' inherit this function to add delivery date of sale order line into computation formula of date_expedted'''
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        sale_line_id = values.get('sale_line_id', False)
        if sale_line_id:
            sale_line = self.env['sale.order.line'].browse(sale_line_id)
            compute_date_expected =  sale_line.delivery_date and\
                                     datetime.combine(sale_line.delivery_date, datetime.min.time()) \
                                     or fields.Datetime.from_string(values['date_planned'])
            date_expected = fields.Datetime.to_string(compute_date_expected - relativedelta(days=self.delay or 0))
            res.update({
                'date': date_expected,
                'date_expected': date_expected,
            })
        return res