from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo import fields


class TestCreateSaleOrder(TestSale):

    def test_create_sale_order_with_owner(self):
        print ('====== SALE ORDER WITH OWNER ======')
        partner = self.env.ref('base.res_partner_1')
        owner = self.env.ref('base.res_partner_2')
        
        product_a = self.env.ref('product.product_product_6')
        product_b = self.env.ref('product.product_product_8')

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'state': 'draft',
            'invoice_status': 'no',
            'date_order': fields.Datetime.now(),
            'picking_policy': 'direct',
        })
        order_line_a = self.env['sale.order.line'].create({
            'name': product_a.name,
            'product_id': product_a.id,
            'product_uom_qty': 10,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'price_unit': product_a.lst_price,
            'owner_id': owner.id,
            'order_id': sale_order.id,
        })
        order_line_b = self.env['sale.order.line'].create({
            'name': product_b.name,
            'product_id': product_b.id,
            'product_uom_qty': 10,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'price_unit': product_b.lst_price,
            'owner_id': False,
            'order_id': sale_order.id,
        })
        sale_order.action_confirm()

        self.assertTrue(sale_order)
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(len(sale_order.order_line), 2, 'Sale: Order line 2')

        for line in sale_order.order_line:
            if line.owner_id:
                self.assertEqual(line.owner_id.id, owner.id, 'Sale Line: Owner %s' % (owner.name))
            else:
                self.assertEqual(line.owner_id.id, False, 'Sale Line: Owner False')
        
        picking_ids = sale_order.picking_ids
        move_id = self.env['stock.move'].search([('picking_id', '=', picking_ids.id)])
        self.assertTrue(move_id)
        for move in move_id:
            if move.owner_id:
                self.assertEqual(move.owner_id.id, owner.id, 'Stock Move: Owner %s' % (owner.name))
            else:
                self.assertEqual(move.owner_id.id, False, 'Stock Move: Owner False')
            move.write({
                'quantity_done': move.product_uom_qty,
            })
        
        picking_ids.action_assign()

        picking_ids.button_validate()
        
        move_line_id = self.env['stock.move.line'].search([('picking_id', '=', picking_ids.id)])
        self.assertTrue(move_line_id)
        for move_line in move_line_id:
            if move_line.owner_id:
                self.assertEqual(move_line.owner_id.id, owner.id, 'Stock Move: Owner %s' % (owner.name))
            else:
                self.assertEqual(move_line.owner_id.id, False, 'Stock Move: Owner False')

    def test_create_sale_order_without_owner(self):
        print ('====== SALE ORDER WITHOUT OWNER ======')
        partner = self.env.ref('base.res_partner_1')
        owner = self.env.ref('base.res_partner_2')
        
        product_a = self.env.ref('product.product_product_6')
        product_b = self.env.ref('product.product_product_8')

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'state': 'draft',
            'invoice_status': 'no',
            'date_order': fields.Datetime.now(),
            'picking_policy': 'direct',
        })
        order_line_a = self.env['sale.order.line'].create({
            'name': product_a.name,
            'product_id': product_a.id,
            'product_uom_qty': 10,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'price_unit': product_a.lst_price,
            'owner_id': False,
            'order_id': sale_order.id,
        })
        order_line_b = self.env['sale.order.line'].create({
            'name': product_b.name,
            'product_id': product_b.id,
            'product_uom_qty': 10,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'price_unit': product_b.lst_price,
            'owner_id': False,
            'order_id': sale_order.id,
        })
        sale_order.action_confirm()

        self.assertTrue(sale_order)
        self.assertTrue(sale_order.picking_ids)
        self.assertEqual(len(sale_order.order_line), 2, 'Sale: Order line 2')

        for line in sale_order.order_line:
            if not line.owner_id:
                self.assertEqual(line.owner_id.id, False, 'Sale Line: Owner False')
        
        picking_ids = sale_order.picking_ids
        move_id = self.env['stock.move'].search([('picking_id', '=', picking_ids.id)])
        self.assertTrue(move_id)
        for move in move_id:
            if not move.owner_id:
                self.assertEqual(move.owner_id.id, False, 'Stock Move: Owner False')
            move.write({
                'quantity_done': move.product_uom_qty,
            })
        
        picking_ids.action_assign()

        picking_ids.button_validate()
        
        move_line_id = self.env['stock.move.line'].search([('picking_id', '=', picking_ids.id)])
        self.assertTrue(move_line_id)
        for move_line in move_line_id:
            if not move_line.owner_id:
                self.assertEqual(move_line.owner_id.id, False, 'Stock Move: Owner False')
