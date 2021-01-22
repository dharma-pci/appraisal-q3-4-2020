# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import odoo.tests
from odoo import fields, api
from datetime import datetime
from odoo.tests import tagged, Form
from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon


@odoo.tests.tagged('post_install', '-at_install')
class TestMultiPaymentInvoice(odoo.tests.TransactionCase):

    def setUp(self):
        super(TestMultiPaymentInvoice, self).setUp()
        self.product_ids = self.env['product.product'].browse([15,19,14,21,6])
        self.azure = self.env.ref("base.res_partner_12")
        self.deco = self.env.ref("base.res_partner_2")
        self.immediate = self.env.ref('account.account_payment_term_immediate')
        self.days15 = self.env.ref('account.account_payment_term_15days')
        self.revenue = self.env.ref("account.data_account_type_revenue")
        self.account_revenue = self.env["account.account"].search(
            [
                ("user_type_id", "=", self.revenue.id)
            ], 
            limit=1
        )
        self.move = self.env['account.move']
        self.date_now = datetime.now().date()
        value = {
            'partner_id': self.azure.id, 
            'invoice_payment_term_id': self.immediate.id, 
            'invoice_date': self.date_now, 
            "type": "out_invoice",
            "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
            'ref': '',
            'invoice_line_ids':[(0, 0, {
                'name': self.product_ids[0].name, 
                'product_id': self.product_ids[0].id, 
                'quantity': 1, 
                "account_id": self.account_revenue.id,
                'price_unit': self.product_ids[0].lst_price
            })]
        }
        self.move_id1 = self.move.create(value)
        value = {
            'partner_id': self.azure.id, 
            'invoice_payment_term_id': self.immediate.id, 
            'invoice_date': self.date_now, 
            "type": "out_invoice",
            "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
            'ref': '',
            'invoice_line_ids':[
                (0, 0, {
                'name': self.product_ids[0].name,
                'product_id': self.product_ids[0].id, 
                'quantity': 2, 
                "account_id": self.account_revenue.id,
                'price_unit': self.product_ids[0].lst_price}), 
                (0, 0, {
                'name': self.product_ids[0].name,
                'product_id': self.product_ids[1].id, 
                'quantity': 1, 
                "account_id": self.account_revenue.id,
                'price_unit': self.product_ids[0].lst_price})
            ]
        }
        self.move_id2 = self.move.create(value)
        value = {
            'partner_id': self.deco.id, 
            'invoice_payment_term_id': self.immediate.id, 
            'invoice_date': self.date_now, 
            "type": "out_invoice",
            "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
            'ref': '',
            'invoice_line_ids':[
                (0, 0, {
                'name': self.product_ids[0].name,
                'product_id': self.product_ids[0].id, 
                'quantity': 1, 
                "account_id": self.account_revenue.id,
                'price_unit': self.product_ids[0].lst_price}), 
                (0, 0, {
                'name': self.product_ids[0].name,
                'product_id': self.product_ids[1].id, 
                'quantity': 2, 
                "account_id": self.account_revenue.id,
                'price_unit': self.product_ids[1].lst_price})
            ]
        }
        self.move_id3 = self.move.create(value)
        self.account_journal = self.env['account.journal'].browse(7)

    def test_single_payment(self):
        """
        single payment
        """
        self.move_id1.action_post()
        self.assertEqual(self.move_id1.state, 'posted', "Posted / already post")
        value = {
            'payment_date': datetime.now().date(), 
            'journal_id': self.account_journal.id, 
            'payment_method_id': self.account_journal.inbound_payment_method_ids[0].id, 
            'invoice_ids': self.move_id1.ids, 
            'group_payment': False,
        }
        register = self.env['account.payment.register'].create(value)
        ctx = register.create_payments()
        regiter_payment = self.env['account.payment'].search(ctx.get('domain'))
        payment = regiter_payment.post()
        self.assertTrue(payment)
        self.assertEqual(
            regiter_payment.state, 
            'posted', 
            "Posted / already post"
        )
        self.assertEqual(
            self.move_id1.amount_total, 
            regiter_payment.amount, 
            "Total Invoice"
        )

    def test_double_payment(self):
        """
        double payments
        """
        # ========double payment with group=======
        self.move4 = self.move_id1.copy()
        self.move_id2.action_post()
        self.move_id3.action_post()
        self.move4.action_post()
        self.assertEqual(
            self.move_id2.state, 
            'posted', 
            "Posted / already post"
        )
        self.assertEqual(
            self.move_id3.state, 
            'posted',
            "Posted / already post"
        )
        self.assertEqual(
            self.move4.state, 
            'posted', 
            "Posted / already post"
        )
        value = {
            'payment_date': datetime.now().date(), 
            'journal_id': self.account_journal.id, 
            'payment_method_id': self.account_journal.inbound_payment_method_ids[0].id, 
            'invoice_ids': [self.move_id2.id, self.move_id3.id, self.move4.id], 
            'group_payment': True,
        }
        register = self.env['account.payment.register'].create(value)
        ctx = register.create_payments()
        regiter_payment = self.env['account.payment'].search(ctx.get('domain'))
        self.assertEqual(
            regiter_payment[0].partner_id.id, 
            self.deco.id, 
            "Posted / already post"
        )
        self.assertEqual(
            regiter_payment[1].partner_id.id, 
            self.azure.id, 
            "Posted / already post"
        )
        self.assertEqual(
            self.move_id3.amount_total, 
            regiter_payment[0].amount, 
            "Total Invoice"
        )
        self.assertEqual(
            '%.2f' % (self.move_id2.amount_total + self.move4.amount_total), 
            '%.2f' % (regiter_payment[1].amount), 
            "Total Invoice"
        )
        # ========double payment with out group=======
        self.move5 = self.move_id1.copy()
        self.move6 = self.move_id2.copy()
        self.move7 = self.move_id3.copy()
        self.move5.action_post()
        self.move6.action_post()
        self.move7.action_post()
        self.assertEqual(
            self.move5.state, 
            'posted', 
            "Posted / already post"
        )
        self.assertEqual(
            self.move6.state, 
            'posted', 
            "Posted / already post"
        )
        self.assertEqual(
            self.move7.state, 
            'posted', 
            "Posted / already post"
        )
        value = {
            'payment_date': datetime.now().date(), 
            'journal_id': self.account_journal.id, 
            'payment_method_id': self.account_journal.inbound_payment_method_ids[0].id, 
            'invoice_ids': [self.move5.id, self.move6.id, self.move7.id], 
            'group_payment': False,
        }
        register = self.env['account.payment.register'].create(value)
        ctx = register.create_payments()
        regiter_payment = self.env['account.payment'].search(ctx.get('domain'))
        self.assertEqual(
            '%.2f' % (self.move7.amount_total), 
            '%.2f' % (regiter_payment[0].amount), 
            "Total Invoice"
        )
        self.assertEqual(
            '%.2f' % (self.move6.amount_total), 
            '%.2f' % (regiter_payment[1].amount), 
            "Total Invoice"
        )
        self.assertEqual(
            '%.2f' % (self.move5.amount_total), 
            '%.2f' % (regiter_payment[2].amount), 
            "Total Invoice"
        )
