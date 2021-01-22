
from odoo import api, fields, models, _
from itertools import groupby



class StockMove(models.Model):
    _inherit = 'stock.move'


    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        grouped_moves = groupby(sorted(self, key=lambda m: [f.id for f in m._key_assign_picking()]), key=lambda m: [m._key_assign_picking()])
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*list(moves))
            new_picking = False
            picking = moves[0]._search_picking_for_assignation()
            if picking:
                if any(picking.partner_id.id != m.partner_id.id or
                        picking.origin != m.origin for m in moves):
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
                    moves.write({'picking_id': picking.id})
                    moves._assign_picking_post_process(new=new_picking)
        return True
