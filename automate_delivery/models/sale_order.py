from odoo import fields, models, _


class SaleOrderLine(models.Model):
    """ inherit model sale order line """
    _inherit = 'sale.order.line'

    owner_id = fields.Many2one('res.partner', string='Owner',)

    def _prepare_procurement_values(self, group_id=False):
        """ inherit function _prepare_procurement_values for adding new field """
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({
            'owner_id': self.owner_id.id,
        })
        return values