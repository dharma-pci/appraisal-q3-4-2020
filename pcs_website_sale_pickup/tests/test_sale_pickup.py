import odoo.tests

from odoo import api
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tests import tagged, Form
from odoo.addons.website.tools import MockRequest

@odoo.tests.tagged('post_install', '-at_install')
class TestWebsiteSalePickup(odoo.tests.TransactionCase):
    
    def setUp(self):
        super(TestWebsiteSalePickup, self).setUp()
        self.SaleOrder = self.env['sale.order']
        self.free_delivery_product = self.env.ref('delivery.product_product_delivery')
        self.website = self.env['website'].browse(1)
        self.country_id = self.env['res.country'].search([], limit=1).id
        self.WebsiteSaleController = WebsiteSale()
        self.product_uom_unit = self.env.ref('uom.product_uom_unit')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.free_delivery = self.env.ref("delivery.free_delivery_carrier")

    def _active_personal_pickup(self, partner_id=None):
    	self.env.ref("delivery.free_delivery_carrier").write({
            'personal_pickup': True,
            'message_alert': 'Not Available this time!',
        })

    def _create_so(self, partner_id=None):
        return self.env['sale.order'].create({
            'partner_id': partner_id,
            'website_id': self.website.id,
            'order_line': [(0, 0, {
                'product_id': self.env['product.product'].create({
                	'name': 'Website Product', 
                	'list_price': 10,
                	}).id,
                'name': 'Product A',
                'product_uom_qty': 1, 
            }), (0, 0, {
                'name': 'Free Delivery',
                'product_id': self.free_delivery_product.id,
            })]
        })

    def test_01_check_carrier(self):
        self._active_personal_pickup()

        self.assertTrue(self.free_delivery.personal_pickup)
        self.assertTrue(self.free_delivery.message_alert)

    def test_02_so_free_delivery(self):
        p = self.env.user.partner_id
        order = self._create_so(p.id)

        order.carrier_id = self.free_delivery.id
        order.personal_pickup_location = self.warehouse.id

        self.assertTrue(self._create_so)
        self.assertTrue(order.personal_pickup_location)
        self.assertEqual(len(order.order_line), 2, "Free Delivery product Added")
        self.assertEqual(order.personal_pickup_location.id, self.free_delivery.id, "Personal Pickup Warehouse ")
        self.assertEqual(order.carrier_id.id, self.env.ref("delivery.free_delivery_carrier").id, "Pickup from store carrier")
        self.assertEqual(order.website_id.id, self.website.id, "SO from Website")