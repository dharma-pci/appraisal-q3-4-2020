import odoo
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError




class LeadProducts(models.Model):
    _name = 'crm.purchase.product'
    _description = 'CRM Purchase Product'

    lead_id = fields.Many2one('crm.lead')
    product_id = fields.Many2one('product.product',
                                 required=True, change_default=True)
    request_qty = fields.Float(string='Request Quantity',
                               digits='Product Unit of Measure', required=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                                     domain="[('category_id', '=', product_uom_category_id)]")
    partner_ids = fields.Many2many('res.partner', string='Vendor', required=True,
                                   change_default=True)
    qty_available = fields.Float(related='product_id.qty_available', string='Quantity on Hand')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    po_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line',
                                 copy=False)
    po_id = fields.Many2one('purchase.order', string='Purchase Order',
                                 related='po_line_id.order_id')

    # Product available vendors, used in dynamic domain of vendor in product line
    product_partner_ids = fields.Many2many(related='product_id.partner_ids')

    # Vendor of product line, stored as o2m to use in search of line's vendor in CRM
    line_partner_id = fields.Many2one('res.partner', string='Line\'s Vendor',
                                      compute='_compute_line_partner_id', store=True)

    @api.depends('partner_ids')
    def _compute_line_partner_id(self):
        """ Store selected Vendor of line from m2m into m2o field
            This m2o field will use to read by a related field in CRM
            to enable the searching on Line's Vendor
        """
        for rec in self:
            vendor = False
            if rec.partner_ids:
                vendor = rec.partner_ids[0].id
            rec.line_partner_id = vendor

    @api.constrains('request_qty')
    def _check_request_qty_not_zero(self):
        """ Validate Request Quantity input
        """
        for rec in self:
            if rec.request_qty < 1:
                raise ValidationError(_('"Request Quantity" should be greater than 0.'))

    @api.constrains('partner_ids')
    def _check_partner_ids_single_input(self):
        """ Validate Vendor for single input
        """
        for rec in self:
            if len(rec.partner_ids) > 1:
                raise ValidationError(_('Please choose only one vendor in Vendor column.'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ On change of Product, suggest available vendors and set the UoM
        """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_po_id or self.product_id.uom_id

            sellers = self.product_id.seller_ids.mapped('name.id')
            self.partner_ids = sellers
        else:
            self.product_uom_id = False
            self.partner_ids = False

    def _validate_seller_price(self, vals):
        """ Validate if selected product vendor have Price in purchase seller
            Check at least one seller of vendor must have price
        """
        vendor_data = vals.get('partner_ids')
        product_obj = self.env['product.product']
        product = product_obj.browse(vals.get('product_id'))
        if vendor_data and product:
            vendor = vendor_data[0][2][0]
            seller_list = product.seller_ids.filtered(
                lambda l: l.name.id == vendor)
            sellers_with_price = seller_list.filtered(lambda l: l.price != 0)
            if not sellers_with_price:
                raise ValidationError(_('Please set the Price of vendor "%s" for product "%s".')
                                      %(seller_list[0].name.name, product.name))
            vals.update({
                'price_unit': sellers_with_price[0].price
            })
        return vals

    def write(self, vals):
        vals = self._validate_seller_price(vals)
        return super(LeadProducts, self).write(vals)
  
    @api.model
    def create(self, vals):
        vals = self._validate_seller_price(vals)
        return super(LeadProducts, self).create(vals)
