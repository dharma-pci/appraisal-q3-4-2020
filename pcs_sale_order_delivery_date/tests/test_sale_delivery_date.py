from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo import fields

class TestSaleDeliveryDate(TestSale):
    
    def test_without_delivery_date(self):
        """test confirm so with blank delivery date"""
        partner = self.env.ref('base.res_partner_1')
        product_1 = self.env.ref('product.product_delivery_01')
        product_2 = self.env.ref('product.product_delivery_02')

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'state': 'draft',
            'invoice_status': 'no',
        })
        order_line_1 = self.env['sale.order.line'].create({
            'name': product_1.name,
            'product_id': product_1.id,
            'product_uom_qty': 10,
            'product_uom': product_1.uom_id.id,
            'order_id': sale_order.id,
            'price_unit': product_1.list_price
        })
        order_line_2 = self.env['sale.order.line'].create({
            'name': product_2.name,
            'product_id': product_2.id,
            'product_uom_qty': 20,
            'product_uom': product_2.uom_id.id,
            'order_id': sale_order.id,
            'price_unit': product_2.list_price
        })
        sale_order.action_confirm()
        num_of_delivery = len(sale_order.picking_ids.filtered(lambda pick: pick.state in ['confirmed']))
        print('test confirm sale without delivery date')
        self.assertEqual(num_of_delivery, 1, 'Number of delivery should be 1.0 instead of %s'%(num_of_delivery))
    
    def test_with_same_delivery_date(self):
        """test confirm so with same delivery date"""
        partner = self.env.ref('base.res_partner_1')
        product_1 = self.env.ref('product.product_delivery_01')
        product_2 = self.env.ref('product.product_delivery_02')

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'state': 'draft',
            'invoice_status': 'no',
        })
        order_line_1 = self.env['sale.order.line'].create({
            'name': product_1.name,
            'product_id': product_1.id,
            'product_uom_qty': 10,
            'product_uom': product_1.uom_id.id,
            'order_id': sale_order.id,
            'price_unit': product_1.list_price,
            'delivery_date': fields.Date.today(),
        })
        order_line_2 = self.env['sale.order.line'].create({
            'name': product_2.name,
            'product_id': product_2.id,
            'product_uom_qty': 20,
            'product_uom': product_2.uom_id.id,
            'order_id': sale_order.id,
            'price_unit': product_2.list_price,
            'delivery_date': fields.Date.today(),
        })
        sale_order.action_confirm()
        num_of_delivery = len(sale_order.picking_ids.filtered(lambda pick: pick.state in ['confirmed']))
        print('test confirm sale with same delivery date')
        self.assertEqual(num_of_delivery, 1, 'Number of delivery should be 1.0 instead of %s'%(num_of_delivery))
    
    def test_with_different_delivery_date(self):
        """test confirm so with different delivery date"""
        partner = self.env.ref('base.res_partner_1')
        product_1 = self.env.ref('product.product_delivery_01')
        product_2 = self.env.ref('product.product_delivery_02')

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'state': 'draft',
            'invoice_status': 'no',
        })
        order_line_1 = self.env['sale.order.line'].create({
            'name': product_1.name,
            'product_id': product_1.id,
            'product_uom_qty': 10,
            'product_uom': product_1.uom_id.id,
            'order_id': sale_order.id,
            'price_unit': product_1.list_price,
            'delivery_date': fields.Date.today(),
        })
        order_line_2 = self.env['sale.order.line'].create({
            'name': product_2.name,
            'product_id': product_2.id,
            'product_uom_qty': 20,
            'product_uom': product_2.uom_id.id,
            'order_id': sale_order.id,
            'price_unit': product_2.list_price,
            'delivery_date': fields.Date.today()+relativedelta(days=1),
        })
        sale_order.action_confirm()
        num_of_delivery = len(sale_order.picking_ids.filtered(lambda pick: pick.state in ['confirmed']))
        print('test confirm sale with different delivery date')
        self.assertEqual(num_of_delivery, 2, 'Number of delivery should be 2.0 instead of %s'%(num_of_delivery))