# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    penalty_type = fields.Selection(
        [('amount', 'Penalty Amount'), ('percent', 'Penalty Percentage')], 
        string="Penalty Type", 
    )
    penalty_amount = fields.Float(string="Penalty Amount")
    penalty_amount_percent = fields.Float(string="Penalty Amount (%)")
    penalty_due_date = fields.Selection([
            ('0', 'On Due Date'),
            ('5', '5 Days after Due Date'),
            ('10', '10 Days after Due Date')
        ], string="Penalty Due Date",
        default='0'
    )
    penalty_product_id = fields.Many2one('product.product', 
        string="Penalty Product", 
        default=lambda self: self.env.ref('pcs_invoice_penalty.penalty_product', \
            raise_if_not_found=False),
    )
