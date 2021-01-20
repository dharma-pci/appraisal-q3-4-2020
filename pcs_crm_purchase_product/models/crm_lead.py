import odoo
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError




class Lead(models.Model):
    _inherit = 'crm.lead'

    crm_products_ids = fields.One2many('crm.purchase.product', 'lead_id',
                                       string="Request Product to Vendor", ondelete='cascade')
    purchase_count = fields.Integer(compute='_compute_linked_purchases',
                                    string='Purchase Count')

    # Enable to search product line columns in CRM
    product_id = fields.Many2one(related='crm_products_ids.product_id')
    line_partner_id = fields.Many2one(related='crm_products_ids.line_partner_id')

    def _get_linked_po(self):
        po_ids = self.crm_products_ids.mapped('po_id.id') or []
        return po_ids

    def _compute_linked_purchases(self):
        for rec in self:
            po_ids = rec._get_linked_po()
            rec.purchase_count = len(po_ids)

    def action_view_purchase_rfq(self):
        """ Action to open all RFQs linked to the CRM
        """
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]

        # choose the view_mode accordingly
        po_ids = self._get_linked_po()
        if len(po_ids) > 1:
            result['domain'] = "[('id', 'in', " + str(po_ids) + ")]"
        else:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = po_ids[0]
        return result

    def _get_updated_origin(self, rfq_rec):
        origin = rfq_rec.origin or ''
        origin_to_add = self.name
        seprator = ""
        if origin:
            seprator = ", "
        if origin_to_add not in origin:
            origin = (_('%s%s%s') %(origin, seprator, origin_to_add))
        return origin

    def _create_new_rfq(self, partner_id):
        """ Create new RFQ by given partner
        """
        po_obj = self.env['purchase.order'].sudo()
        new_po = po_obj.create({
            'partner_id': partner_id,
            'company_id': self.env.company.id
        })
        return new_po

    def _create_new_rfq_line_from_crm_line(self, crm_product_line, rfq_rec):
        """ Create new line in RFQ from CRM product line
        """
        pol_obj = self.env['purchase.order.line'].sudo()
        new_line = pol_obj.create({
            'name': (_('[%s] %s') %(crm_product_line.product_id.default_code, crm_product_line.product_id.name)),
            'product_id': crm_product_line.product_id.id,
            'product_uom': crm_product_line.product_uom_id.id,   
            'product_qty': crm_product_line.request_qty,
            'price_unit': crm_product_line.price_unit,
            'date_planned': fields.Date.today(),
            'company_id': self.env.company.id,
            'order_id': rfq_rec.id
        })
        crm_product_line.sudo().write({
            'po_line_id': new_line.id
        })
        return new_line

    def _create_vendor_rfq_from_crm_lines(self, crm_product_lines, exist_rfq):
        """ Create RFQs crm product lines with grouped vendors
        """
        rfq_to_process = exist_rfq
        if not rfq_to_process:
            partner_id = crm_product_lines[0].line_partner_id.id
            rfq_to_process = self._create_new_rfq(partner_id)

        order_lines = []
        for line in crm_product_lines:
            new_line = self._create_new_rfq_line_from_crm_line(line, rfq_to_process)
            order_lines.append((4, new_line.id))

        origin = self._get_updated_origin(rfq_to_process)
        rfq_to_process.sudo().write({
            'order_line': order_lines,
            'origin': origin
        })

    def _check_rfq_exist(self, vendor):
        """ Check if RFQ corresponding vendor exist
        """
        po_obj = self.env['purchase.order'].sudo()
        exist_rfq = po_obj.search([('partner_id', '=', vendor),
                                   ('state', 'in', ('draft', 'sent')),
                                   ('company_id', '=', self.env.company.id)])
        return exist_rfq

    def action_add_product_lines(self):
        """ Input new product lines in pop up """
        self.ensure_one()
        ctx = self._context.copy()
        active_id = self.id or self._context.get('active_id')
        ctx['active_id'] = active_id
        return {
            'name': _("Add Product Lines to Purchase"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('pcs_crm_purchase_product.add_crm_product_lines_view_form').id,
            'res_model': 'crm.lead',
            'res_id': active_id,
            'target': 'new',
            'context': ctx
        }

    def action_create_vendor_rfq(self):
        """ - Create new RFQs based on grouped vendor
                - Only lines which not linked to any RFQ will take into account to generate new RFQs
                - If the vendor already exist in any RFQ, system will append the new lines to the exist RFQ
                - By default, process will not merge the duplicate product lines and
                  consider them as separate lines
        """
        self.ensure_one()
        crm_product_lines = self.crm_products_ids

        # Validate if there is any new line to generate the RFQs
        all_lines_to_process = crm_product_lines.filtered(
            lambda l: not l.po_line_id)
        if not all_lines_to_process:
            raise ValidationError(_('Please add some new lines to process.'))

        vendor_list = crm_product_lines.mapped('line_partner_id.id')
        for vendor in vendor_list:
            lines_to_process = all_lines_to_process.filtered(
                lambda l: l.line_partner_id.id == vendor)
            if lines_to_process:
                exist_rfq = self._check_rfq_exist(vendor)
                self._create_vendor_rfq_from_crm_lines(lines_to_process, exist_rfq[0] if exist_rfq else False)
