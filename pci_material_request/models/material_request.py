from odoo import api, fields, models, _

class MaterialRequest(models.Model):
    """ New Model material.request """
    _name = "material.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Material Request"

    name = fields.Char(
        string='Name',
        required=True,
        copy=False,
        default='New',
        readonly=True,
        tracking=True
    )
    date = fields.Datetime(string="Date", default=fields.Datetime.now())
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('done', 'Approve'),
            ('cancel', 'Cancel')
        ],
        'Status',
        tracking=True,
        required=True,
        copy=False,
        default='draft'
    )
    request_line_ids = fields.One2many(
        'material.request.line',
        'request_id',
        string='Request Lines',
        copy=True
    )
    mrp_production_id = fields.Many2one('mrp.production')

    @api.model
    def create(self, vals):
        """ Create sequence """
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date' in vals:
                seq_date = fields.Date.from_string(vals.get('date'))
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'material.request', sequence_date=seq_date) or 'New'
        return super(MaterialRequest, self).create(vals)

    def action_confirm(self):
        """
        Change state to Confirm
        """
        self.state = 'confirm'

    def action_approve(self):
        """ Change state to Done """
        mrp_production = self.mrp_production_id
        moves_raw_values = mrp_production._get_moves_raw_values()
        list_move_raw = []
        for move_raw_values in moves_raw_values:
            move_raw_values['product_uom_qty'] = self.get_real_quantity(move_raw_values['product_id'])
            list_move_raw += [(0, 0, move_raw_values)]
        mrp_production.move_raw_ids = list_move_raw
        self.state = 'done'

    def action_cancel(self):
        """ Change state back to draft """
        self.state = 'draft'
    
    def get_real_quantity(self, product_id):
        """get real real quantity on material request"""
        mrl = self.env['material.request.line']
        real_qty = mrl.search([('product_id', '=', product_id), ('request_id', '=', self.id)], limit=1)
        if real_qty:
            return real_qty.actual_product_uom_qty
        return 0.0


class MaterialRequestLine(models.Model):
    """ Model Material Request Line """
    _name = "material.request.line"
    _description = "Material Request Line"
    _rec_name = 'product_id'

    request_id = fields.Many2one(
        'material.request',
        required=True,
        index=True,
        string='Material Request',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    
    planned_product_uom_qty = fields.Float(
        string='Plan Quantity',
        digits='Product Unit of Measure',
    )
    actual_product_uom_qty = fields.Float(
        string='Actual Quantity',
        digits='Product Unit of Measure',
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        'Unit of Measure',
        track_visibility='onchange'
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Set product UoM """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

