from datetime import datetime

from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools.translate import _




class TestCrmPurchaseProduct(TransactionCase):
    """ Test CRM Purchase Product Class """

    def setUp(self):
        """ Setup data to Test """
        super(TestCrmPurchaseProduct, self).setUp()
        # UoM Unit
        self.uom_unit_id = self.ref('uom.product_uom_unit')
        # Create products to use in CRM lines
        self.category = self.env['product.category'].create({
            'name': 'Category A',
            'property_cost_method': 'standard',
            'property_valuation': 'manual_periodic',
        })
        # Create 5 different products
        def _create_product(name):
            res = self.env['product.product'].create({
                'name': name,
                'type': 'product',
                'categ_id': self.category.id,
                'uom_id': self.uom_unit_id,
                'purchase_ok': True
            })
            return res
        self.product_a = _create_product('Product A')
        self.product_b = _create_product('Product B')
        self.product_c = _create_product('Product C')
        self.product_d = _create_product('Product D')
        self.product_e = _create_product('Product E')
        # Create new partners A, B, C
        partner_obj = self.env['res.partner']
        self.partner_a = partner_obj.create({
            'name': 'Partner A',
            'company_type': 'company',
        })
        self.partner_b = partner_obj.create({
            'name': 'Partner B',
            'company_type': 'company',
        })
        self.partner_c = partner_obj.create({
            'name': 'Partner C',
            'company_type': 'company',
        })
        # Create RFQ with partner_a to consider as the exist one
        picking_type_obj = self.env['stock.picking.type']
        company_id = self.ref('base.main_company')
        currency_id = self.ref('base.USD')
        self.po_obj = self.env['purchase.order']
        self.exist_rfq = self.po_obj.create({
            'partner_id': self.partner_b.id,
            'date_order': datetime.now(),
            'currency_id': currency_id,
            'company_id': company_id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_a.id,
                    'name': self.product_a.name,
                    'product_uom': self.uom_unit_id,   
                    'product_qty': 2,
                    'price_unit': 100,
                    'date_planned': datetime.now()
                })
            ]
        })
        # Create price lists for products A, B, C, D
        # Product E will test without pricelist
        self.product_a.write({'seller_ids': [
            (0, 0, {'name': self.partner_a.id, 'price': 200}),
            (0, 0, {'name': self.partner_b.id, 'price': 150}),
        ]})
        self.product_b.write({'seller_ids': [
            (0, 0, {'name': self.partner_a.id, 'price': 100}),
            (0, 0, {'name': self.partner_b.id, 'price': 170}),
            (0, 0, {'name': self.partner_c.id, 'price': 0}),
        ]})
        self.product_c.write({'seller_ids': [
            (0, 0, {'name': self.partner_a.id, 'price': 220}),
        ]})
        self.product_d.write({'seller_ids': [
            (0, 0, {'name': self.partner_b.id, 'price': 350}),
            (0, 0, {'name': self.partner_c.id, 'price': 120}),
        ]})
        # Create Lead
        default_stage_id = self.ref("crm.stage_lead1")
        crm_obj = self.env['crm.lead']
        self.crm_opp_01 = crm_obj.create({
            'type': 'opportunity',
            'name': 'Test opportunity 1',
            'partner_id': self.partner_a.id,
            'stage_id': default_stage_id,
            'description': 'This is the description of the test opp 1.'
        })

    def _get_new_linked_po(self):
        po_ids = self.crm_opp_01._get_linked_po()
        po_rec = self.po_obj.browse(po_ids)
        return po_rec

    def _get_rfq_count(self):
        po_rec = self._get_new_linked_po()
        return len(po_rec)

    def _get_processing_rfq(self, domain):
        return self.po_obj.search(domain)

    def _get_exist_rfq_count(self):
        domain = ['|',
                  ('origin', '=', 'Test opportunity 1'),
                  ('id', '=', self.exist_rfq.id)
        ]
        return self.po_obj.search_count(domain)

    def _get_new_created_rfq(self):
        domain = [('origin', '=', 'Test opportunity 1')]
        rfq = self._get_processing_rfq(domain)
        return rfq

    def _test_asserts(self, expected_rfq_count, msg_param, rfq):
        exist_rfq_lines_count = len(rfq.order_line) if rfq else 0
        # Process creating the RFQ(s)
        self.crm_opp_01.action_create_vendor_rfq()

        linked_rfq_in_crm = self._get_rfq_count()
        if not rfq:
            rfq = self._get_new_created_rfq()
        exist_rfq_lines_new_count = len(rfq.order_line)
        all_rfq = self._get_exist_rfq_count()

        self.assertEqual(linked_rfq_in_crm, 1, (_("Linking CRM to the %s RFQ failed.") %(msg_param)))
        self.assertEqual(all_rfq, expected_rfq_count, (_("Creating product line of CRM into %s RFQ failed.") %(msg_param)))
        self.assertNotEqual(exist_rfq_lines_count, exist_rfq_lines_new_count, (_("Product line of CRM failed to create in %s RFQ.") %(msg_param)))

    def test_create_rfq_line_in_exist_rfq(self):
        self.crm_opp_01.write({
            'crm_products_ids': [
                (0, 0, {
                    'product_id': self.product_d.id,
                    'request_qty': 1,
                    'product_uom_id': self.product_a.uom_id.id,
                    'partner_ids': [[6, False, [self.product_d.seller_ids[0].name.id]]],
                })
            ]
        })
        domain = [('id', '=', self.exist_rfq.id)]
        rfq = self._get_processing_rfq(domain)
        self._test_asserts(1, 'exist', rfq)

    def test_create_rfq_line_in_new_rfq(self):
        self.crm_opp_01.write({
            'crm_products_ids': [
                (0, 0, {
                    'product_id': self.product_c.id,
                    'request_qty': 2,
                    'product_uom_id': self.product_a.uom_id.id,
                    'partner_ids': [[6, False, [self.product_c.seller_ids[0].name.id]]],
                })
            ]
        })
        self._test_asserts(2, 'new', False)
