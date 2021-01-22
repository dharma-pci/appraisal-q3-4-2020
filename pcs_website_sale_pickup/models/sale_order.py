import odoo

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    personal_pickup_location = fields.Many2one('stock.warehouse', string="Pick up from store")