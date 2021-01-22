
from odoo import api, fields, models, _
from odoo.tools.profiler import profile
[...]



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @profile
    def create_delivery_order(self):
        """ Function to display the Wizard and send data to wizard as well through Context """
        view = self.env.ref('pcs_sale_order_partial_delivery.delivery_order_wizard_view_form')

        return {
            'name': _('Create Delivery Order'),
            'view_mode': 'form',
            'res_model': 'delivery.order.wizard',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'type': 'ir.actions.act_window',
            'context': {'default_sale_order_id': self.id, 'default_order_line': False},
            'target': 'new',
        }
    

        