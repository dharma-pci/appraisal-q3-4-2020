from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class MrpProduction(models.Model):
    """ inherit mrp.production """
    _inherit = "mrp.production"
    
    material_request_id = fields.Many2one('material.request')

    @api.model
    def create(self, values):
        """
        trigger Material Request creation
        """
        res = super(MrpProduction, self).create(values)
        material_request = self.env['material.request']
        material_request_line = self.env['material.request.line']
        bom_line_ids = res.bom_id.bom_line_ids
        component = []
        mr = material_request.create({
            'mrp_production_id':res.id,
        })
        res.material_request_id = mr.id
        for line in bom_line_ids:
            material_request_line.create({
                'request_id':mr.id,
                'product_id':line.product_id.id,
                'planned_product_uom_qty':line.product_qty,
                'product_uom_id':line.product_uom_id.id,
            })
        return res

    @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id')
    def _onchange_move_raw(self):
        """disable raw material creation on change bom id"""
        res = super(MrpProduction, self)._onchange_move_raw()
        self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids]
        return res
        

    