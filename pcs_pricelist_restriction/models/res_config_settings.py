# -*- coding: utf-8 -*-
""" Res Config Settings """
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """ Inherit Res Config Settings """

    _inherit = 'res.config.settings'

    pricelist_restriction = fields.Selection(
        [('user', 'For User'), ('partner', 'For Partner')],
        default='user', config_parameter='pcs_pricelist_restriction.pricelist_restriction')
