from odoo import fields,models,api,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_move_ids = fields.Many2many('stock.move','stock_picking_move_rel','so_id','stock_move_id',compute='_compute_picking_move_ids')
    picking_move_count = fields.Integer(string='Delivery Order',compute='_count_picking_move_ids')

    @api.depends('order_line','order_line.picking_move_ids')
    def _compute_picking_move_ids(self):
        for order in self:
            if order.order_line.picking_move_ids:
                moves_ids = order.order_line.mapped('picking_move_ids').ids
                order.picking_move_ids = [(6,0,moves_ids)]
            else:
                order.picking_move_ids = [(6, 0, [])]


    @api.depends('picking_move_ids')
    def _count_picking_move_ids(self):
        for order in self:
            picking_obj = self.env['stock.picking']
            picking_ids = picking_obj + order.order_line.picking_move_ids.mapped('picking_id') + order.picking_ids
            order.picking_move_count = len(list(set(picking_ids)))

    def action_view_delivery_order(self):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        picking_moves = self.order_line.picking_move_ids.mapped('picking_id')
        pickings = self.mapped('picking_ids') + picking_moves
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id, default_picking_id=picking_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    picking_move_ids = fields.One2many('stock.move','sale_line_id')