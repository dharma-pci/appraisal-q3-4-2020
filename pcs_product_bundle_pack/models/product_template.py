from odoo import api, fields, models

class ProductTemplate(models.Model):
    _description = "Product Template"
    _inherit = "product.template"

    is_product_pack = fields.Boolean()
    is_calculate_pack_price = fields.Boolean()
    product_pack_ids = fields.One2many('product.pack', 'product_tmpl_id', string='Pack Products')

    @api.model
    def create(self, vals):
        """ Call function calculate total pack price if boolean product pack true and boolean calculate pack price true """
        res = super(ProductTemplate, self).create(vals)
        for rec in self:
            if vals.get('is_calculate_pack_price', False) and vals.get('is_product_pack',False):
                total_price = self.calculate_total_pack_price(rec.product_pack_ids)
                res.list_price = total_price
        return res

    def write(self, vals):
        """ Call function calculate total pack price if boolean product pack true and boolean calculate pack price true """
        res = super(ProductTemplate, self).write(vals)
        for rec in self:
            if vals.get('is_calculate_pack_price', False) or (self.is_calculate_pack_price and not vals.get('is_calculate_pack_price',False) and vals.get('product_pack_ids')):
                total_price = self.calculate_total_pack_price(rec.product_pack_ids)
                rec.update({
                    'list_price': total_price
                })
        return res

    def calculate_total_pack_price(self,product_pack_ids):
        """ Function to calculate total pack price"""
        total_price = 0
        if product_pack_ids:
            qty_list = product_pack_ids.mapped('quantity')
            lst_price_list = product_pack_ids.mapped('product_id').mapped('lst_price')
            total_price =  sum([lst_price_list[i] * qty_list[i] for i in range(len(product_pack_ids))])
        return total_price