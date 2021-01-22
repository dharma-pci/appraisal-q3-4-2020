# from odoo import fields,models,api,_

# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     picking_move_count = fields.Integer(string='Delivery Order',compute='_count_picking_move_ids')

#     @api.depends('order_line','order_line.move_ids')
#     def _count_picking_move_ids(self):
#         for order in self:
#             picking_obj = self.env['stock.picking']
#             picking_ids = picking_obj + order.order_line.move_ids.mapped('picking_id')
#             order.picking_move_count = len(list(set(picking_ids)))

#     def action_view_picking_order(self):
#         """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
#         """
#         picking_obj = self.env['stock.picking']
#         action = self.env.ref('stock.action_picking_tree_all')
#         result = action.read()[0]
#         # override the context to get rid of the default filtering on operation type
#         result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name, 'default_picking_type_id': self.picking_type_id.id}
#         picking_moves = picking_obj.search([('purchase_id.id','=',self.id)])
#         pick_ids = self.mapped('picking_ids') + picking_moves
#         # choose the view_mode accordingly
#         if not pick_ids or len(pick_ids) > 1:
#             result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
#         elif len(pick_ids) == 1:
#             res = self.env.ref('stock.view_picking_form', False)
#             form_view = [(res and res.id or False, 'form')]
#             if 'views' in result:
#                 result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
#             else:
#                 result['views'] = form_view
#             result['res_id'] = pick_ids.id
#         return result