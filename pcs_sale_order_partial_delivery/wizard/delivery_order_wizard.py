
from odoo import api, fields, models
from odoo.tools.profiler import profile
[...]


class DeliveryOrderWizard(models.TransientModel):
    """ Create new wizard function name delivery.order.wizard """


    _name = 'delivery.order.wizard'
    


    order_line = fields.One2many('delivery.order.wizard.line', 'delivery_order_id', string='Order Lines')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order Reference", store=True, readonly=True)

    @profile
    def _get_order_line_data(self):
        """ Get data from Order line """
        sale_order_id = self.env.context.get('default_sale_order_id')
        so_records = self.env['sale.order'].search([('id','=',sale_order_id)])
        vals = []
        
        for line in so_records.order_line:
            vals.append((0, 0, {'company_id': line.company_id.id,
                                        'name':line.name,
                                        'product_id':line.product_id.id,
                                        'product_uom_qty': line.product_uom_qty,
                                        'price_unit': line.price_unit}))
        return vals
        
    @profile
    @api.model
    def default_get(self, fields):
        """ Set the default order_line field to fill with data from _get_order_line_data() function """
        res = super(DeliveryOrderWizard, self).default_get(fields)
        res['order_line'] = self._get_order_line_data()
        return res

    @profile
    def generate_delivery_order(self):
        """ Function to create new Delivery Order when click on Generate button in pop-up wizard """
        move_list = []
        moves = False
        Picking = self.env['stock.picking']
        
        for line in self.sale_order_id.order_line:
            stock_move = self.env['stock.move'].search([('product_id','=',line.product_id.id)]).filtered(
                lambda x:x.sale_line_id.order_id.id == line.order_id.id)
            move_list.append(stock_move)

        moves = self.env['stock.move'].concat(*list(move_list))  
        new_picking = Picking.create(moves._get_new_picking_values())
        moves.write({'picking_id' : new_picking.id})

        for record in moves:
            record.write({'quantity_done': record.product_qty})
        moves.picking_id.button_validate()


        