''' sale.order '''
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    """ inherit sale.order.line """

    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one(
        'product.pricelist')

    @api.onchange('product_id')
    def product_id_change(self):
        ''' extend function to change price based on selected pricelist '''

        res = super(SaleOrderLine, self).product_id_change()
        vals = {}
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.pricelist_id.id,
            uom=self.product_uom.id
        )
        if self.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        ''' extend function to change price based on selected pricelist '''

        res = super(SaleOrderLine, self).product_uom_change()
        vals = {}
        if self.pricelist_id and self.order_id.partner_id:
            self.price_unit = 0
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id, self.tax_id, self.company_id)
            self.update(vals)
        return res

    def pricelist_change(self):
        ''' function for change price unit when apply multiple pricelist '''

        vals = {}
        if self.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id, self.tax_id, self.company_id)
            self.update(vals)

    def _get_display_price(self, product):
        ''' extend to change return pricelist '''

        res = super(SaleOrderLine, self)._get_display_price(product)
        if self.pricelist_id and self.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.pricelist_id.id).price
        return res

    def action_select_pricelist(self):
        ''' update price based on selected pricelist '''

        view_id = self.env.ref('sale_multi_pricelist.pricelist_selection_view_form')

        pricelist_ids = self.env['product.pricelist'].search([])
        vals = []
        for pricelist in pricelist_ids:
            vals.append(([0, 0, {'pricelist_id': pricelist.id}]))

        wiz_vals = {
            'sale_line_id': self.id,
            'pricelist_id': self.pricelist_id.id,
            'line_ids': vals
        }
        wiz_id = self.env['pricelist.selection'].create(wiz_vals)
        return {
            'name': _('Select Pricelist'),
            'view_mode': 'form',
            'res_model': 'pricelist.selection',
            'view_id': view_id.id,
            'res_id': wiz_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

