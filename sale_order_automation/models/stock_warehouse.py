# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Warehouse(models.Model): 
    """ Inherit model stock.warehouse """
    _inherit = "stock.warehouse"

    automated_picking_creation = fields.Boolean("Automated Picking Creation", help="Create Picking when confirm Quotation")
    automated_picking_validation = fields.Boolean("Automated Picking Validation", help="Validate Picking when Confirm Quotation")

    automated_invoice_creation = fields.Boolean("Automated Inoice Creation", help="Create Invoice when confirm Quotation / validated Picking")
    create_invoice_triger = fields.Selection([
                                ("sale","Sale"),
                                ("picking", "Picking")],string="Create Invoice Trigger", default="sale", help="Select this one to trigger create invoice")
    
    automated_invoice_validation = fields.Boolean("Automated Invoice Validation", help="Validate Invoice When Confirm Qoutation / Validate Picking")



    @api.onchange("automated_picking_creation")
    def _onchange_automated_picking_creation(self):
        if not self.automated_picking_creation:
            self.automated_picking_validation = False

    @api.onchange("automated_invoice_creation")
    def _onchange_automated_invoice_creation(self):
        if not self.automated_invoice_creation:
            self.create_invoice_triger = "sale"
            self.automated_invoice_validation = False