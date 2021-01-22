from odoo import fields,models,api,_
from odoo.exceptions import UserError

class MergePicking(models.TransientModel):
    _name = 'merge.picking'
    _description = 'Merge Picking'

    picking_ids = fields.Many2many('stock.picking')

    @api.model
    def default_get(self, default_fields):
        rec = super(MergePicking, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id').ids
        rec.update({
            'picking_ids': [(6,0,active_ids)]
        })
        return rec
    
    def validate_picking(self):
        # We can not merge one single picking.
        # We can not merge already done pickings.
        # We can not merge different partners picking.
        # We can merge only pickings that are ready (state).
        # We can merge only with the same operation type picking.
        if len(self.picking_ids) == 1:
            raise UserError(_("Can't merge because single picking"))
        elif self.picking_ids.filtered(lambda x: x.state == 'done'):
            raise UserError(_("Can't merge because any picking allready done"))
        elif len(list(set(self.picking_ids.mapped('partner_id')))) > 1:
            raise UserError(_("Can't merge because have different partner"))
        elif len(list(set(self.picking_ids.mapped('state')))) > 1:
            raise UserError(_("Can't Merge because have different state"))
        elif self.picking_ids.filtered(lambda x: x.state != 'assigned'):
            raise UserError(_("Can't Merge because have picking not ready"))
        elif len(list(set(self.picking_ids.mapped('picking_type_code')))) > 1:
            raise UserError(_("Can't Merge because have different type picking"))
        elif not self.picking_ids:
            raise UserError(_("Can't Merge because don't have picking"))

    # Header Picking
    def picking_value(self):
        picking_id = self.picking_ids[0]
        picking_type_id = picking_id.picking_type_id
        location_id = picking_id.location_id
        location_dest_id = picking_id.location_dest_id
        partner_id = picking_id.partner_id
        return {
                'picking_type_id': picking_type_id.id,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'partner_id': partner_id.id if partner_id else False,
                'origin': str(set(self.picking_ids.mapped('name'))).replace('{','').replace('}','').replace("'",''),
                'move_line_ids_without_package': [],
                'move_ids_without_package': [],
                'package_level_ids_details': [],
            }

    def merge_picking(self):
        # Validate Picking
        self.validate_picking()
        
        # Create Picking
        picking_id = self.env['stock.picking'].create(self.picking_value())
        
        picking_ids = self.picking_ids

        # Move stock.move to new picking
        stock_move_ids = picking_ids.mapped('move_ids_without_package')
        for move in stock_move_ids:
            move.picking_id = picking_id
        
        # Move stock.move.line to new picking
        stock_move_lines_ids = picking_ids.mapped('move_lines')
        for lines in stock_move_lines_ids:
            lines.picking_id = picking_id

        picking_id.do_unreserve()
        picking_id.action_assign()

        
        # Cancel old picking
        for pick in picking_ids:
            pick.action_cancel()
            pick.state = 'cancel'
        
        return {
            'name': _('Inventory'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'res_id': picking_id.id,
        }