import odoo
from odoo import api, fields, models
from odoo.tools.translate import _




class ProductProduct(models.Model):
    _inherit = 'product.product'

    partner_ids = fields.Many2many('res.partner', compute='_compute_partner_ids',
                                   string='Product Vendors',
                                   compute_sudo=True, store=True)

    @api.depends('seller_ids', 'seller_ids.name')
    def _compute_partner_ids(self):
        """ Mapped vendors from product seller_ids to use in
            'Vendor' column's dynamic domain of CRM
        """
        for rec in self:
            rec.partner_ids = rec.seller_ids.mapped('name.id')
