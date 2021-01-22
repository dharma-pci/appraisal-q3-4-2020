from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _description = "Sale Order Line"
    _inherit = "sale.order.line"

    def _get_outgoing_incoming_moves_bundle(self):
        """ Get outgoing & incoming moves product bundle"""
        outgoing_moves = self.env['stock.move']
        incoming_moves = self.env['stock.move']

        if self.product_id.is_product_pack:
            for product_pack in self.product_id.product_pack_ids:
                for move in self.move_ids.filtered(lambda r: r.state != 'cancel' and not r.scrapped and product_pack.product_id == r.product_id):
                    if move.location_dest_id.usage == "customer":
                        if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                            outgoing_moves |= move
                    elif move.location_dest_id.usage != "customer" and move.to_refund:
                        incoming_moves |= move

        return outgoing_moves , incoming_moves

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        """ Inherit this function to compute qty delivered for product bundle of the SO lines """
        super(SaleOrderLine, self)._compute_qty_delivered()

        for line in self: 
            if line.qty_delivered_method == 'stock_move' and line.product_id.is_product_pack:
                qty = 0.0
                outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves_bundle()
                for move in outgoing_moves:
                    if move.state != 'done':
                        continue
                    qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                for move in incoming_moves:
                    if move.state != 'done':
                        continue
                    qty -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
                line.qty_delivered = line.product_uom_qty if qty == sum(line.product_id.product_pack_ids.mapped('quantity')) * line.product_uom_qty else 0.0