# -*- coding: utf-8 -*-
""" Sale Order """
from odoo import fields, models, api


class SaleOrder(models.Model):
    """ Inherit Sale Order """

    _inherit = 'sale.order'

    allowed_pricelist_ids = fields.Many2many(
        'product.pricelist', 'sale_order_product_pricelist_rel',
        'sale_id', 'pricelist_id', compute='_compute_allowed_pricelist')
    # redefine field; remove domain
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="[]",
        help="If you change the pricelist, only newly added lines will be affected.")

    @api.depends('partner_id', 'company_id')
    def _compute_allowed_pricelist(self):
        """ Compute Allowed Pricelist """

        get_restriction = self.env['ir.config_parameter'].sudo().get_param(
            'pcs_pricelist_restriction.pricelist_restriction')
        restriction = 'user' if not get_restriction or get_restriction == 'user' else 'partner'
        for order in self:
            all_price = []
            company = order.company_id or self.env.company
            if restriction == 'partner' and order.partner_id:
                all_price = order.partner_id.partner_pricelist_ids.filtered(
                    lambda r: not r.company_id or r.company_id == company).ids
            elif restriction == 'user':
                all_price = self.env.user.user_pricelist_ids.ids
            order.update({'allowed_pricelist_ids': [(6, 0, all_price)]})            

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """ Inherit Onchange Partner Id """

        res = super(SaleOrder, self).onchange_partner_id()
        # update pricelist to prevent inconsistency domain
        if self.pricelist_id and self.allowed_pricelist_ids \
            and self.pricelist_id in self.allowed_pricelist_ids:
            pricelist = self.pricelist_id.id
        elif self.allowed_pricelist_ids:
            pricelist = self.allowed_pricelist_ids.ids[0]
        else:
            pricelist = False        
        self.update({'pricelist_id': pricelist})
        return res
