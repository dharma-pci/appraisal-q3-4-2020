from odoo import api, fields, models


class DeliveryOrderWizardLine(models.TransientModel):
    """ Create Wizard Model delivery order wizard line """

    _name = 'delivery.order.wizard.line'


    company_id = fields.Many2one('res.company', string="Company", readonly=True)
    delivery_order_id = fields.Many2one('delivery.order.wizard', string="Delivery order", readonly=True)
    name = fields.Text(string='Description', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0, readonly=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0, readonly=True)