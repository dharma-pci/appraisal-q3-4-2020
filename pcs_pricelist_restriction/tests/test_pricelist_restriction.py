# -*- coding: utf-8 -*-
""" Test Pricelist Restriction """
from odoo.tests import common


class TestPricelist(common.TransactionCase):
    """ Class unit testing partner activity """

    def setUp(self):
        """ Define global variable """

        super(TestPricelist, self).setUp()

        # define users
        group_user = self.browse_ref('sales_team.group_sale_manager')
        self.sales_mng = self.env['res.users'].with_context({'no_reset_password': True}).create({
            'name': 'Sales',
            'login': 'sales',
            'email': 'sales@email.com',
            'groups_id': [(6, 0, [group_user.id])]})

        self.partner = self.browse_ref('base.res_partner_12')
        self.partner2 = self.browse_ref('base.res_partner_2')
        currency = self.browse_ref('base.USD')
        self.pricelist1 = self.env['product.pricelist'].create(
            {'name': 'pricelist1', 'currency_id': currency.id})
        self.pricelist2 = self.env['product.pricelist'].create(
            {'name': 'pricelist2', 'currency_id': currency.id})
        self.pricelist3 = self.env['product.pricelist'].create(
            {'name': 'pricelist3', 'currency_id': currency.id})
        self.applied_pricelist = [self.pricelist1.id, self.pricelist2.id, self.pricelist3.id]

    def apply_user_restriction(self):
        """ Apply Pricelist Restriction by User """

        conf = self.env['res.config.settings'].create({'pricelist_restriction': 'user'})
        conf.execute()

    def apply_partner_restriction(self):
        """ Apply Pricelist Restriction by Partner """

        conf = self.env['res.config.settings'].create({'pricelist_restriction': 'partner'})
        conf.execute()

    def assign_pricelist(self):
        """ Assigning Pricelist """

        active_ids = [self.partner.id, self.partner2.id]
        wiz = self.env['assign.pricelist.wizard'].with_user(self.sales_mng).create(
            {'pricelist_ids': [(6, 0, self.applied_pricelist)]})
        wiz.with_user(self.sales_mng).with_context(active_ids=active_ids).assign_pricelist()

    def test_assign_pricelist(self):
        """ Test Assign Pricelist """

        self.assign_pricelist()
        self.assertEqual(self.partner.partner_pricelist_ids.ids, self.applied_pricelist,
                         "Incorrect pricelist assignment for partner 1")
        self.assertEqual(self.partner2.partner_pricelist_ids.ids, self.applied_pricelist,
                         "Incorrect pricelist assignment for partner 2")

    def test_reset_pricelist(self):
        """ test Reset Pricelist """

        self.assign_pricelist()
        partners = self.partner
        partners |= self.partner2
        partners.with_user(self.sales_mng).action_reset_pricelist()
        self.assertEqual(self.partner.partner_pricelist_ids.ids, [],
                         "Incorrect value for resetting pricelist of partner 1")
        self.assertEqual(self.partner2.partner_pricelist_ids.ids, [],
                         "Incorrect value for resetting pricelist of partner 2")

    def test_user_restriction(self):
        """ Test Pricelist Restriction by User """

        self.apply_user_restriction()
        self.sales_mng.write({'user_pricelist_ids': [(6, 0, [self.pricelist1.id, self.pricelist2.id])]})
        # test pricelist visibility in pricelist menu
        all_pricelist = sorted(self.env['product.pricelist'].with_user(
            self.sales_mng).with_context(restrict_pricelist=True).search([]).ids)
        self.assertEqual(len(all_pricelist), 2,
                         "Incorrect numbers of allowed pricelists for user")
        self.assertEqual(all_pricelist, [self.pricelist1.id, self.pricelist2.id],
                         "Incorrect values of allowed pricelists for user")
        # test allow pricelist in order
        orders = self.env['sale.order'].with_user(self.sales_mng).new({'partner_id': self.partner.id})
        self.assertEqual(len(orders.allowed_pricelist_ids), 2,
                         "Incorrect numbers of allowed pricelists for user in orders")
        order_pricelist = sorted(orders.allowed_pricelist_ids.ids)
        self.assertEqual(order_pricelist, [self.pricelist1.id, self.pricelist2.id],
                         "Incorrect values of allowed pricelists for user in orders")

    def test_partner_restriction(self):
        """ Test Pricelist Resrtriction by Partner """

        self.apply_partner_restriction()
        self.partner.write({'partner_pricelist_ids': [(6, 0, [self.pricelist2.id, self.pricelist3.id])]})
        # test allow pricelist in order
        orders = self.env['sale.order'].with_user(self.sales_mng).new({'partner_id': self.partner.id})
        self.assertEqual(len(orders.allowed_pricelist_ids), 2,
                         "Incorrect numbers of allowed pricelists for user in orders")
        order_pricelist = sorted(orders.allowed_pricelist_ids.ids)
        self.assertEqual(order_pricelist, [self.pricelist2.id, self.pricelist3.id],
                         "Incorrect values of allowed pricelists for user in orders")
