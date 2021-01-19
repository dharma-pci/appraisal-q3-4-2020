# coding: utf-8
from odoo import api, fields, models, _
from odoo.tools.profiler import profile


class PosOrder(models.Model):
    _inherit = "pos.order"

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
            