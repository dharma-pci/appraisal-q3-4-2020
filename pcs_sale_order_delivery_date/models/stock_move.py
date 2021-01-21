from itertools import groupby
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'
    delivery_date = fields.Date('Delivery Date', related="sale_line_id.delivery_date")

    def _search_picking_for_assignation(self):
        '''Replace base function to add scheduled date into search parameter'''
        self.ensure_one()
        picking = self.env['stock.picking'].search([
                    ('group_id', '=', self.group_id.id),
                    ('location_id', '=', self.location_id.id),
                    ('location_dest_id', '=', self.location_dest_id.id),
                    ('picking_type_id', '=', self.picking_type_id.id),
                    ('printed', '=', False),
                    ('immediate_transfer', '=', False),
                    ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned']),
                    ('scheduled_date', '>=', self.date_expected),
                    ('scheduled_date', '<', self.date_expected + relativedelta(days=1)),
                ], limit=1)
        return picking
    
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        res.update({
            'scheduled_date': min(self.mapped('date_expected'))
        })
        return res
    
    def _assign_picking(self):
        """ Replace base function to add parameter delivery date on grouping"""
        Picking = self.env['stock.picking']
        grouped_moves = groupby(sorted(self, key=lambda m: [f.id for f in m._key_assign_picking()]), key=lambda m: [m.date_expected, m._key_assign_picking()])
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*list(moves))
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()
            if picking:
                if any(picking.partner_id.id != m.partner_id.id or
                        picking.origin != m.origin for m in moves):
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                new_picking = True
                picking = Picking.create(moves._get_new_picking_values())

            moves.write({'picking_id': picking.id})
            moves._assign_picking_post_process(new=new_picking)
        return True
    