from odoo.tools import float_is_zero
from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart
from odoo.tests import Form


class TestSaleToInvoice(TestCommonSaleNoChart):

    @classmethod
    def setUpClass(cls):
        super(TestSaleToInvoice, cls).setUpClass()

        cls.setUpClassicProducts()
        cls.setUpAdditionalAccounts()
        cls.setUpAccountJournal()

        # Create the SO with four order lines
        cls.sale_order = cls.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id': cls.partner_customer_usd.id,
            'partner_invoice_id': cls.partner_customer_usd.id,
            'partner_shipping_id': cls.partner_customer_usd.id,
            'pricelist_id': cls.pricelist_usd.id,
        })
        SaleOrderLine = cls.env['sale.order.line'].with_context(tracking_disable=True)
        cls.sol_prod_order = SaleOrderLine.create({
            'name': cls.product_order.name,
            'product_id': cls.product_order.id,
            'product_uom_qty': 5,
            'product_uom': cls.product_order.uom_id.id,
            'price_unit': cls.product_order.list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })
        SaleServiceLine = cls.env['sale.service.line'].with_context(tracking_disable=True)
        cls.sol_serv_deliver = SaleServiceLine.create({
            'name': cls.service_deliver.name,
            'product_id': cls.service_deliver.id,
            'product_uom_qty': 4,
            'product_uom': cls.service_deliver.uom_id.id,
            'price_unit': cls.service_deliver.list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })

        # Context
        cls.context = {
            'active_model': 'sale.order',
            'active_ids': [cls.sale_order.id],
            'active_id': cls.sale_order.id,
            'default_journal_id': cls.journal_sale.id,
        }

    def test_invoice(self):
        """ Test create and invoice from the SO, and check qty invoice/to invoice, and the related amounts """
        # lines are in draft
        for line in self.sale_order.order_line:
            self.assertTrue(float_is_zero(line.untaxed_amount_to_invoice, precision_digits=2), "The amount to invoice should be zero, as the line is in draft state")
            self.assertTrue(float_is_zero(line.untaxed_amount_invoiced, precision_digits=2), "The invoiced amount should be zero, as the line is in draft state")

        # Confirm the SO
        self.sale_order.action_confirm()

        # Check ordered quantity, quantity to invoice and invoiced quantity of SO lines
        for line in self.sale_order.order_line:
            if line.product_id.invoice_policy == 'delivery':
                self.assertEquals(line.qty_to_invoice, 0.0, 'Quantity to invoice should be same as ordered quantity')
                self.assertEquals(line.qty_invoiced, 0.0, 'Invoiced quantity should be zero as no any invoice created for SO')
                self.assertEquals(line.untaxed_amount_to_invoice, 0.0, "The amount to invoice should be zero, as the line based on delivered quantity")
                self.assertEquals(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as the line based on delivered quantity")
            else:
                self.assertEquals(line.qty_to_invoice, line.product_uom_qty, 'Quantity to invoice should be same as ordered quantity')
                self.assertEquals(line.qty_invoiced, 0.0, 'Invoiced quantity should be zero as no any invoice created for SO')
                self.assertEquals(line.untaxed_amount_to_invoice, line.product_uom_qty * line.price_unit, "The amount to invoice should the total of the line, as the line is confirmed")
                self.assertEquals(line.untaxed_amount_invoiced, 0.0, "The invoiced amount should be zero, as the line is confirmed")

        # Let's do an invoice with invoiceable lines
        payment = self.env['sale.advance.payment.inv'].with_context(self.context).create({
            'advance_payment_method': 'split_invoice'
        })
        payment.create_invoices()

