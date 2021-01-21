from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_date = fields.Date('Delivery Date')