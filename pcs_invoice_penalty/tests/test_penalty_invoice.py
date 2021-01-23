# -*- coding: utf-8 -*-
from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon
from odoo.tests.common import Form
from odoo.tests import tagged
from odoo import fields
from odoo.exceptions import UserError

from unittest.mock import patch
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)


# @tagged('post_install', '-at_install')
class TestPenaltyInvoice(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.invoice_1 = cls.init_invoice('out_invoice', invoice_date='2021-01-01')
        cls.invoice_2 = cls.init_invoice('out_invoice', invoice_date='2021-01-03')
        cls.invoice_3 = cls.init_invoice('out_invoice', invoice_date='2021-01-05')
    
    def test_penalty_invoice_amount(self):
        invoice_obj = self.env['account.move']
        invoice_1 = self.invoice_1
        invoice_2 = self.invoice_2
        invoice_3 = self.invoice_3

        invoice_1.action_post()
        invoice_2.action_post()
        invoice_3.action_post()

        company = invoice_1.company_id
        company.write({
            'penalty_type': 'amount',
            'penalty_amount': 100,
            'penalty_due_date': '0',
            'penalty_product_id': self.env.ref('pcs_invoice_penalty.penalty_product'),
        })
        invoice_obj.with_context(check_date='2021-01-02').get_penalty_invoice()
        # Check count of penalty invoice created
        self.assertEqual(invoice_1.penalty_invoice_count, 1)
        self.assertEqual(invoice_2.penalty_invoice_count, 0)
        self.assertEqual(invoice_3.penalty_invoice_count, 0)
        # Check amount of penalty invoice
        if self.assertEqual(invoice_1.penalty_invoice_count, 1):
            penalty_invoice = invoice_1.penalty_invoice_ids[0]
            self.assertEqual(penalty_invoice.amount_total, 100)

    
    def test_penalty_invoice_amount_percent(self):
        invoice_obj = self.env['account.move']
        invoice_1 = self.invoice_1
        invoice_2 = self.invoice_2
        invoice_3 = self.invoice_3

        invoice_1.action_post()
        invoice_2.action_post()
        invoice_3.action_post()

        company = invoice_1.company_id
        company.write({
            'penalty_type': 'percent',
            'penalty_amount': 10,
            'penalty_due_date': '0',
            'penalty_product_id': self.env.ref('pcs_invoice_penalty.penalty_product'),
        })
        invoice_obj.with_context(check_date='2021-01-04').get_penalty_invoice()
        # Check count of penalty invoice created
        self.assertEqual(invoice_1.penalty_invoice_count, 1)
        self.assertEqual(invoice_2.penalty_invoice_count, 1)
        self.assertEqual(invoice_3.penalty_invoice_count, 0)
        # Check amount of penalty invoice
        if self.assertEqual(invoice_1.penalty_invoice_count, 1):
            penalty_invoice = invoice_1.penalty_invoice_ids[0]
            self.assertEqual(penalty_invoice.amount_total, 141)

