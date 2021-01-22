from odoo import api, fields, models

class ProcurementGroup(models.Model):
    _description = 'Procement Group'
    _inherit = 'procurement.group'

    @api.model
    def run(self, procurements):
        """ Inherit this function if 'run' is called on a bundle, this override is made in order to call
        the original 'run' method with the values of the components of that bundle.
        """
        procurements_product_pack = []
        for procurement in procurements:
            if procurement.product_id.is_product_pack:
                product_packs = procurement.product_id.product_pack_ids
                line = self.env['sale.order.line'].browse(procurement.values.get('sale_line_id',False))
                for product_pack in product_packs:
                    product_id = product_pack.product_id
                    product_uom = product_id.uom_id
                    product_qty = product_pack.quantity * line.product_uom_qty
                    values = dict(procurement.values, product_pack_id=product_pack.id)
                    procurements_product_pack.append(self.env['procurement.group'].Procurement(
                        product_id, product_qty, product_uom,
                        procurement.location_id, procurement.name,
                        procurement.origin, procurement.company_id, values))
            else:
                procurements_product_pack.append(procurement)
        return super(ProcurementGroup, self).run(procurements_product_pack)

        
