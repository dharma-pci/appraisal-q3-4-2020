# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    """ Inherit model stock.picking """
    _inherit = "stock.picking"

    def action_done(self):
        """
            inherit this function for checking boolean in warehouse to create invoice automatic
        """
        res = super(StockPicking, self).action_done()
        for record in self:
            if record.sale_id.warehouse_id.automated_invoice_creation and record.sale_id.warehouse_id.create_invoice_triger == "picking":
                record.sale_id._create_invoices(final=True)
        return res