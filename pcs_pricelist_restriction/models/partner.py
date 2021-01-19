# -*- coding: utf-8 -*-
""" Partner """
from odoo import fields, models


class ResPartner(models.Model):
    """ Inherit Res Partner """

    _inherit = 'res.partner'

    partner_pricelist_ids = fields.Many2many(
        'product.pricelist', 'partner_product_pricelist_rel',
        'partner_id', 'pricelist_id', string='Partner Price List')

    def action_reset_pricelist(self):
        """ Reset Pricelist """

        self.write({'partner_pricelist_ids': [(6, 0, [])]})
