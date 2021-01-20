# coding: utf-8
from odoo import api, fields, models, _
from odoo.tools.profiler import profile


class PosOrder(models.Model):
    _inherit = "pos.order"

    pos_return_from = fields.Many2one('pos.order', string='Return From')
    # get order that search by name or pos reference and must total not lower than zero 
    # this function will be called in js pos screen
    [...]
    @profile
    @api.model
    def get_order_search(self, search_query):
        order = self.env['pos.order'].search_read(['|', ('name','=',search_query), ('pos_reference','ilike',search_query), ('amount_total','>',0)])
        if order:
            return order
        else:
            return False

    # function search orderline by given order id
    # this function will be called by js
    [...]
    @profile
    @api.model
    def get_order_line_search(self, order_id):
        orderlines = self.env['pos.order.line'].search_read([('order_id','=',int(order_id))])
        if orderlines:
            return orderlines
        else:
            return False

    # make each coupon is consume each used
    [...]
    @profile
    @api.model
    def _process_order(self, order, draft, existing_order):
        res = super(PosOrder, self)._process_order(order, draft, existing_order)
        # created pos order will check each orderline coupon_id
        new_order = order['data']
        lines = new_order.get('lines')
        for line in lines:
            if line[2].get('from_return_line_id'):
                order_line = self.env['pos.order.line'].browse(line[2].get('from_return_line_id'))
                order_line.sudo().write({'qty_return':(line[2].get('qty') * -1),}) 
        return res

    [...]
    @profile
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('pos_return_from', False):
            res.update({
                'pos_return_from': ui_order['pos_return_from']
            })
        return res
            
class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    from_return_line_id = fields.Many2one('pos.order.line', string="Return From Pos Line")
    qty_return = fields.Float(string='Qty Returned')