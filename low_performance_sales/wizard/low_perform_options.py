# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LowPerformOptions(models.TransientModel):
    _name = 'low.perform.options'
    _description = 'Low Perform Options'

    report_type = fields.Selection([('product_variant', 'By Product Variant'),
                                    ('product_template', 'By Product Template')],
                                   string='Report Type', default='product_variant')
    date_from = fields.Date()
    date_to = fields.Date()
    critical_level_qty = fields.Integer('Critical Level (Absolute Quantity)')
    critical_level_currency = fields.Integer('Critical Level (Sales in default currency)')
    product_categ_id = fields.Many2one('product.category', 'Product Category')
    sale_team_ids = fields.Many2many('crm.team', 'crm_low_perform_rel',
                                     'crm_team_id', 'low_id', string='Sales Team')
    country_id = fields.Many2one('res.country', string='Partner Country')

    @api.constrains('critical_level_qty', 'critical_level_currency')
    def _check_critical_amount(self):
        for this in self:
            if this.critical_level_qty < 0 or this.critical_level_qty == 0:
                raise UserError(_('Critical Level (Absolute Quantity) '
                                  'Cannot less than zero or equal to zero'))
            if this.critical_level_currency < 0 or this.critical_level_currency == 0:
                raise UserError(_('Critical Level (Sales in default currency) '
                                  'Cannot less than zero or equal to zero'))

    def generate_report_odoo(self):
        pass

    def generate_report_excel(self):
        pass

    def get_data(self):
        pass

    def variant_or_template(self, report_type):
        """
        static function to determine which object will be used
        :param report_type: type of report desired by the user
        :return: object name
        """
        if report_type == 'product_variant':
            return 'product.product'
        else:
            return 'product.template'
