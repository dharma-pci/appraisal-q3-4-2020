# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LowPerformanceSale(models.Model):
    _name = 'low.performance.sale'
    _description = 'Low Performance Sale'

    product_id = fields.Many2one('product.product', 'Product')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    sold_qty = fields.Float('Sold Quantity')
    revenue = fields.Float('Revenue')
