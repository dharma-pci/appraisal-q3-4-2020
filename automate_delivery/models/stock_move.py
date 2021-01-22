from odoo import api, fields, models, _


class StockMove(models.Model):
    """ inherit model stock move """
    _inherit = 'stock.move'

    owner_id = fields.Many2one('res.partner', string='From Owner', store=True, readonly=False)

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        """ inherit function _prepare_merge_moves_distinct_fields for adding new field """
        res = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        res.append('owner_id')
        return res
    
    @api.model
    def _prepare_merge_move_sort_method(self, move):
        """ inherit function _prepare_merge_move_sort_method for adding new field """
        move.ensure_one()
        res = super(StockMove, self)._prepare_merge_move_sort_method(move)
        res.append('move.owner_id')
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """ inherit function _prepare_move_line_vals for adding new field """
        res = super(StockMove, self)._prepare_move_line_vals()
        res.update({
            'owner_id': self.owner_id.id,
        })
        return res

class StockMoveLine(models.Model):
    """ inherit model stock move line """
    _inherit = 'stock.move.line'

    owner_id = fields.Many2one('res.partner', string='From Owner', store=True, readonly=False)

    
