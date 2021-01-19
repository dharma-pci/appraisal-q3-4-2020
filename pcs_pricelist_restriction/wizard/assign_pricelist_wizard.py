# -*- coding: utf-8 -*-
""" Assign Pricelist Wizard """
from odoo import models, fields


class AssignPricelistWizard(models.TransientModel):
    """ Define Assign Pricelist Wizard """

    _name = 'assign.pricelist.wizard'
    _description = 'Assign Pricelist Wizard'

    pricelist_ids = fields.Many2many('product.pricelist')

    def assign_pricelist(self):
        """ Assign Pricelist Into Partner """

        pricelist = self.pricelist_ids.ids or []
        partners = self.env['res.partner'].browse(self._context.get('active_ids'))
        partners.write({'partner_pricelist_ids': [(6, 0, pricelist)]})
