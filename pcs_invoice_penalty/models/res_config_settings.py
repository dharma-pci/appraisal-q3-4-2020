# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    penalty_type = fields.Selection(
        [('amount', 'Penalty Amount'), ('percent', 'Penalty Percentage')], 
        string="Penalty Type", 
        related='company_id.penalty_type',
        readonly=False
    )
    penalty_amount = fields.Float(
        related='company_id.penalty_amount',
        readonly=False
    )
    penalty_amount_percent = fields.Float(
        related='company_id.penalty_amount_percent',
        readonly=False
    )
    penalty_due_date = fields.Selection([
            ('0', 'On Due Date'),
            ('5', '5 Days after Due Date'),
            ('10', '10 Days after Due Date')
        ], string="Penalty Due Date",
        related='company_id.penalty_due_date',
        default='0',
        readonly=False
    )
    penalty_product_id = fields.Many2one(
        'product.product',
        string="Penalty Product",
        default=lambda self: self.env.ref('pcs_invoice_penalty.penalty_product', \
            raise_if_not_found=False),
        related='company_id.penalty_product_id',
        readonly=False
    )
