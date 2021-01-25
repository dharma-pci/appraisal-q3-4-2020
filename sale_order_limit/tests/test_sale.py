import cProfile
import io
import os
import pstats


import random
from odoo.tests.common import Form
from odoo.tests import SavepointCase, tagged
from odoo.exceptions import UserError
from odoo.tools.profiler import profile

import logging
_logger = logging.getLogger(__name__)

RANGE = 30

@tagged('standard','common')
class TestCommon(SavepointCase):

    @classmethod
    def setupPartner(cls):
        Partner = cls.env['res.partner']
        partner_data = {
            'name':"TEST CUSTOMER",
            'email':"customer@mail.com",
            'phone':'081288899999',
            'credit_limit':100, #small limit
            
        }
        cls.customer = Partner.create(partner_data)

        partner_data = {
            'name':"TEST CUSTOMER2",
            'email':"customer@mail.com",
            'phone':'081288899999',
            'credit_limit':200000000,
            
        }
        cls.customer += Partner.create(partner_data)

    @classmethod
    def setupProduct(cls):
        Product = cls.env['product.product']
        FormProduct = Form(Product)

        FormProduct.name = 'TEST PRODUCT'
        FormProduct.type = 'service'
        FormProduct.lst_price = 200000
        FormProduct.invoice_policy = 'order'
        cls.products = FormProduct.save()

        # PORDUCT 2
        Product = cls.env['product.product']
        FormProduct = Form(Product)

        FormProduct.name = 'TEST PRODUCT'
        FormProduct.type = 'service'
        FormProduct.lst_price = 31230000
        FormProduct.invoice_policy = 'order'
        cls.products += FormProduct.save()

        # product3
        Product = cls.env['product.product']
        FormProduct = Form(Product)

        FormProduct.name = 'TEST PRODUCT'
        FormProduct.type = 'service'
        FormProduct.lst_price = 1000000
        FormProduct.invoice_policy = 'order'
        cls.products += FormProduct.save()


    @classmethod
    def setupSaleOrder(cls):
        cls.so = cls.env['sale.order']
        def create_so(customer):
            FormSale = Form(cls.env['sale.order'].with_user(cls.sales_user))
            FormSale.partner_id = customer
            sale = FormSale.save()

            with Form(sale) as so:
                with so.order_line.new() as line:
                    line.product_id = cls.products[0] #only 1 item

            return sale

        cls.so += create_so(cls.customer[0])
        cls.so += create_so(cls.customer[1])

        

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()
        cls.sales_user = cls.env['res.users'].create({
            'name': 'Sales User',
            'login': 'salesuser',
            'email': 'salesuser@yourcompany.com',
            'company_id': cls.env.user.company_id.id,
            
            'groups_id': [(6, 0, [
                cls.env.ref('sales_team.group_sale_salesman').id,
            ])]
        })

        cls.sales_manager = cls.env['res.users'].create({
            'name': 'Sales manager',
            'login': 'salesmanager',
            'email': 'salesmanager@yourcompany.com',
            'company_id': cls.env.user.company_id.id,
            
            'groups_id': [(6, 0, [
                cls.env.ref('sales_team.group_sale_manager').id,
            ])]
        })

        cls.setupPartner()
        cls.setupProduct()
        cls.setupSaleOrder()

    def new_order(self, customers, force_confirm=False, products=None):
        def create_so(customer):
            FormSale = Form(self.env['sale.order'].with_user(self.sales_user))
            FormSale.partner_id = customer
            sale = FormSale.save()

            with Form(sale) as so:
                # beacause we prepare 3 item then set randoom item number to render on order line
                # so will generate various data
                if not products:
                    len_item = random.randrange(len(self.products))
                    if len_item == 0:
                        len_item=1
                    
                    for x in range(len_item):
                        with so.order_line.new() as line:
                            line.product_id = self.products[x]
                
                # if define products
                if products:
                    for p in products:
                        with so.order_line.new() as line:
                            line.product_id = p
                
            if force_confirm:
                # if need to confirm
                sale.with_context(approve_limit=1).action_confirm()
            _logger.info('created so %s with state: %s' % (sale.name, sale.state, ))
            return sale
        res = self.env['sale.order']
        for customer in customers:
            res += create_so(customer)

        return res


    def test_00_limit_validity(self):
        """
        test_00_limit_validity 
        Scenario:
            - self.customer[1].credit_limit == 200,000,000.00

            - create order and invoice related to partner with product[0] with price = 55millions
            - remaining_limit should be 145,000,000.00
            - exceeded_limit is order remaining_limit - total amount of order
        """
        self.products[0].write(dict(lst_price=55000000))
        new_order = self.new_order(self.customer[1], False, self.products[0])



        
        # in this state,, order still in draft,,remaining limit should be still 200millions
        Limit = self.env['partner.credit.limit']
        limit = Limit.find_partner(self.customer[1], low_level=1)

        self.assertTrue(limit[0].get('remaining_credit') == self.customer[1].credit_limit)

        # confirm order with commit saving point
        # because partner.credit.limit is a view sql
        # sometimes will not fetched well during transaction in process
        # so need to savepoint to do a temp commit to be fetched on sql view level
        with self.env.cr.savepoint():
            new_order.with_context(approve_limit=1).action_confirm()
        # when confirming order event it's not invoiced yet then shoudl reduce remaining limit
        limit = Limit.find_partner(self.customer[1], low_level=1)
        self.assertEqual(limit[0].get('remaining_credit'),self.customer[1].credit_limit-new_order.amount_total)

        
        with self.env.cr.savepoint():
            new_order._create_invoices()
        

        limit = Limit.find_partner(self.customer[1], low_level=1)
        self.assertEqual(limit[0].get('remaining_credit'),self.customer[1].credit_limit-new_order.amount_total)


        # post invioce
        with self.env.cr.savepoint():
            new_order.invoice_ids.action_post()

        # should same with prev test
        limit = Limit.find_partner(self.customer[1], low_level=1)
        self.assertEqual(limit[0].get('remaining_credit'),self.customer[1].credit_limit-new_order.amount_total)

        # try pay invoice
        # credit limit should be back to full --> 200millions
        self.journal = self.env['account.journal'] \
            .search([
                ('type', '=', 'cash'), 
                ('company_id', '=', self.env.user.company_id.id),], 
                limit=1
            )

        register_payments = self.env['account.payment.register'] \
            .with_context(active_model='account.move', active_ids=new_order.invoice_ids.ids) \
            .create({
                'journal_id': self.journal.id,
            })
        with self.env.cr.savepoint():
            register_payments._create_payments()
        
        limit = Limit.find_partner(self.customer[1], low_level=1)
        self.assertEqual(limit[0].get('remaining_credit'),self.customer[1].credit_limit)

@tagged('standard','sale')
class TestSale(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSale, cls).setUpClass()
        
    def test_01_confirm_limit_exceeded(self):
        # in this case: partner.credit_limit = 100 / less than order
        # after button confirm clicked then should return action window

        confirm = self.so[0].action_confirm()
        self.assertEqual(self.so[0].state,'draft', "SO State should be still on draft")
        self.assertEqual(type(confirm),dict)
        self.assertTrue(confirm.get('type'),'ir.actions.act_window') #should return window

        self.so[0].with_user(self.sales_user.id).request_limit_approval()
        # so should in waiting approval
        self.assertEqual(self.so[0].state, 'waiting-approval')


        # ensure mail created
        request_mail = self.env['mail.message'] \
            .search([
                ('res_id','=',self.so[0].id),
                ('model','=','sale.order'),
            ],limit=1, order='id desc')
        self.assertEqual(len(request_mail),1) #ensure mail
        self.assertTrue('Waiting Approval - %s' % (self.so[0].name,) in request_mail.subject)
        


        # this session user sales/user try to approve,, should be couldn't
        with self.assertRaises(UserError):
            # should raise UserError
            self.so[0].with_user(self.sales_user.id).approve_credit()

        # approve with sales manager
        self.so[0].with_user(self.sales_manager.id).approve_credit()

        # ensure mail approved created
        approved_mail = self.env['mail.message'] \
            .search([
                ('res_id','=',self.so[0].id),
                ('model','=','sale.order'),
            ],limit=1, order='id desc')
        self.assertEqual(len(approved_mail),1) #ensure mail
        self.assertTrue('APPROVAL - %s' % (self.so[0].name) in approved_mail.subject)
        
        self.assertTrue(self.so[0].state in ('done','sale',)) #DONE!!!


    def test_02_confirm_limit_not_exceeded(self):
        """
        test_02_confirm_limit_not_exceeded Test sale order with partner condition no exceeded limitation
        
        """
        # in this case: partner.credit_limit = None / 0.0

        # after button confirm clicked then should return action window
        
        confirm = self.so[1].action_confirm()
        self.assertTrue(type(confirm)!=dict) # should not return an action dict
        self.assertTrue(self.so[1].state in ('done', 'sale',)) #DONE!!!


    def test_03_confirm_draft_order_limit_exceed_by_manager(self):
        # when manager create and confirm draft order and if partner limit was exceeded then should directly  show pop up then directly move state to "sale order"
        confirm = self.so[0].with_user(self.sales_manager).action_confirm()
        self.assertTrue(type(confirm)==dict) # should return an action dict
        self.assertTrue(self.so[1].state in ('draft', 'sale',)) #still in draft because currently still showing popup
        # manager can clicking "Confirm" button on pop up

        self.so[0].request_limit_approval() # when confirm then directly approved
        
        self.assertTrue(self.so[0].state in ('sale', 'done',))



    

@tagged('standard','performance')
class TestPerformance(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestPerformance, cls).setUpClass()



    def create_orders(self):
        """
        create_orders Create Orders as much as RANGE then create invoice
        """
        orders = self.env['sale.order'] 
        for x in range(RANGE):
            orders += self.new_order(self.customer, True)

        orders._create_invoices()
    
    def request_approval(self, order):
        order.with_user(self.sales_user.id).action_confirm()
    
    
    def test_01_performance(self):
        # self.create_orders()

        with cProfile.Profile() as pr:
            self.request_approval(self.so[0])
            currdir = os.getcwd()
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
            ps.print_stats()

            with open(currdir+'/sale_order_limit/tests/results/profiling/performance.txt', 'w+') as f:
                f.write(s.getvalue())
        