# -*- coding: utf-8 -*-
import time

import odoo
from odoo import fields
from odoo.tools import float_compare, mute_logger, test_reports
from odoo.tests.common import Form
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged('post_install', '-at_install')
class TestPointOfSaleFlow(TestPointOfSaleCommon):

    def test_order_search(self):
        self.pos_config.open_session_cb()
        current_session = self.pos_config.current_session_id
        # I create a new PoS order 
        order = self.PosOrder.create({
            'company_id': self.company_id,
            'session_id': current_session.id,
            'partner_id': self.partner1.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 5.0,
                'qty': 2.0,
                'tax_ids': [(6, 0, self.product3.taxes_id.ids)],
                'price_subtotal': 450 * (1 - 5/100.0) * 2,
                'price_subtotal_incl': 450 * (1 - 5/100.0) * 2,
            })],
            'amount_total': 1710.0,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'pos_reference':'test-001'
        })

        payment_context = {"active_ids": order.ids, "active_id": order.id}
        order_payment = self.PosMakePayment.with_context(**payment_context).create({
            'amount': order.amount_total,
            'payment_method_id': self.cash_payment_method.id
        })
        order_payment.with_context(**payment_context).check()
        # test search pos order
        data_search_by_name = self.env['pos.order'].get_order_search(order.name)
        data_search_by_receipt = self.env['pos.order'].get_order_search(order.pos_reference)
        self.assertEqual(data_search_by_name, data_search_by_receipt, msg='order search must get same result')

        # test search pos order lines
        data_pos_order_line = self.env['pos.order'].get_order_line_search(order.id)
        self.assertEqual(order.lines.read(), data_pos_order_line, msg='Order lines searched must get from order id')

