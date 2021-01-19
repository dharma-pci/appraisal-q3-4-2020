# -*- coding: utf-8 -*-
""" Product Pricelist """
from odoo import fields, models, api


class ProductPricelist(models.Model):
    """ Inherit Product Pricelist """

    _inherit = 'product.pricelist'

    @api.model
    def _search(self, args, offset=0, limit=None,
                order=None, count=False, access_rights_uid=None):
        """ Inherit Search """

        new_args = args or []
        get_restriction = self.env['ir.config_parameter'].sudo().get_param(
            'pcs_pricelist_restriction.pricelist_restriction')
        restriction = 'user' if not get_restriction or get_restriction == 'user' else 'partner'
        # restrict by user configuration
        if self._context.get('restrict_pricelist') and restriction == 'user':
            new_args = [['id', 'in', self.env.user.user_pricelist_ids.ids]] + new_args
        return super(ProductPricelist, self)._search(
            new_args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)
