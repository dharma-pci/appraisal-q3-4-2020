from odoo import api, fields, models
from odoo.exceptions import UserError

class ProductPack(models.Model):
    _description = "Product Pack"
    _name = "product.pack"

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_tmpl_id = fields.Many2one('product.template')
    quantity = fields.Float('Quantity', required=1, default=1)
    image = fields.Binary(string='Image')

    @api.model
    def create(self, vals):
        """Show warning if users input quantity less than 0"""
        if vals.get('quantity', 0) < 0:
            raise UserError('Quantity can not smaller 0')
        return super(ProductPack, self).create(vals)

    def write(self, vals):
        """Show warning if users input quantity less than 0"""
        if vals.get('quantity', 0) < 0:
            raise UserError('Quantity can not smaller 0')
        return super(ProductPack, self).write(vals)