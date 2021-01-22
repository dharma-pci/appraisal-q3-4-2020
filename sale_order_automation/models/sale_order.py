# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    """ Inherit model sale.order """
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False):
        """
            inherit this function for checking boolean in warehouse to validate invoice automatic
        """
        res = super(SaleOrder, self)._create_invoices(grouped=grouped,final=final)
        if self.warehouse_id.automated_invoice_creation and self.warehouse_id.automated_invoice_validation:
            move_id = self.invoice_ids
            for record in move_id:
                if record:
                    record.action_post()
        
        return res

    def action_confirm(self):
        """
            inherit this function for checking boolean in warehouse to validate picking automatic or create invoice 
        """
        res = super(SaleOrder,self).action_confirm()

        automated_picking_creation = self.warehouse_id.automated_picking_creation
        automated_picking_validation = self.warehouse_id.automated_picking_validation

        automated_invoice_creation = self.warehouse_id.automated_invoice_creation
        create_invoice_triger = self.warehouse_id.create_invoice_triger

        picking = self.picking_ids
        if automated_picking_creation and automated_picking_validation:
            for record in picking:
                move_line = record.mapped('move_line_ids_without_package')
                for line in move_line:
                    line.qty_done = line.product_uom_qty
        
            picking.button_validate()
        
        if automated_invoice_creation and create_invoice_triger == "sale":
            self._create_invoices(final=True)
        return res

class SaleOrderLine(models.Model): 
    """ Inherit model sale.order.line """
    _inherit = "sale.order.line"


    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
            inherit this function for checking boolean in warehouse to create picking automatic
        """
        if not self.order_id.warehouse_id.automated_picking_creation:
            return
        
        return super(SaleOrderLine, self)._action_launch_stock_rule(previous_product_uom_qty)