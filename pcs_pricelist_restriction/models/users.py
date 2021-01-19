# -*- coding: utf-8 -*-
""" User """
from odoo import fields, models


class ResUsers(models.Model):
    """ Inherit Res Users """

    _inherit = 'res.users'

    user_pricelist_ids = fields.Many2many(
        'product.pricelist', 'user_product_pricelist_rel',
        'user_id', 'pricelist_id', string='User Price List')
