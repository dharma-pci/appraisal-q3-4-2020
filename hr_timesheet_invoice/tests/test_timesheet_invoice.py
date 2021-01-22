import random
from datetime import datetime

from odoo.tests import common


class TestTimesheetInvoice(common.TransactionCase):

    def setUp(self):
        super(TestTimesheetInvoice, self).setUp()
        # create partners
        partner1 = self.env['res.partner'].create({
            'name': 'partner1'
        })
        partner2 = self.env['res.partner'].create({
            'name': 'partner2'
        })
        self.partners = [partner1, partner2]

        # create some project
        project1 = self.env['project.project'].create({
            'name': 'project1',
            'partner_id': partner1.id,
            'allow_invoice': True,
        })
        project2 = self.env['project.project'].create({
            'name': 'project2',
            'partner_id': partner1.id,
            'allow_invoice': True,
        })
        project3 = self.env['project.project'].create({
            'name': 'project3',
            'partner_id': partner2.id,
            'allow_invoice': False,
        })
        self.projects = [project1, project2, project3]

        # create some employee
        employee1 = self.env['hr.employee'].create({
            'name': 'employee1',
            'timesheet_cost': 100000,
        })
        employee2 = self.env['hr.employee'].create({
            'name': 'employee2',
            'timesheet_cost': 100000,
        })
        employee3 = self.env['hr.employee'].create({
            'name': 'employee3',
            'timesheet_cost': 100000,
        })

        # generate timesheets
        datas = []
        for i in range(0, 100):
            datas.append({
                'date': datetime.now(),
                'employee_id': employee1.id,
                'name': 'desc%s' % i,
                'project_id': project1.id,
                'unit_amount': 1,
            })
        for i in range(100, 200):
            datas.append({
                'date': datetime.now(),
                'employee_id': employee2.id,
                'name': 'desc%s' % i,
                'project_id': project2.id,
                'unit_amount': 1,
            })
        for i in range(200, 300):
            datas.append({
                'date': datetime.now(),
                'employee_id': employee3.id,
                'name': 'desc%s' % i,
                'project_id': project3.id,
                'unit_amount': 1,
            })
        self.timesheets = self.env['account.analytic.line'].create(datas)

    def test_project_allow_invoice(self):
        project1 = self.projects[0]
        self.assertEqual(project1.allow_invoice, True, 'incorrect value of project allow invoice')
        project3 = self.projects[2]
        self.assertEqual(project3.allow_invoice, False, 'incorrect value of project allow invoice')

    def test_timesheet_allow_invoice(self):
        timesheet_first = self.timesheets[0]
        self.assertEqual(timesheet_first.allow_invoice, True, 'incorrect value of timesheet allow invoice')
        timesheet_last = self.timesheets[-1]
        self.assertEqual(timesheet_last.allow_invoice, False, 'incorrect value of timesheet allow invoice')

    def test_generate_invoice_filter_project(self):
        wiz = self.env['invoice.activities.wizard'].create({})
        wiz.project_ids = [(6, 0, [self.projects[0].id])]
        res = wiz.with_context(open_invoices=True).create_invoices()
        self.assertNotEqual(res.get('res_ids'), [], 'failed to generate invoice when filter project')
    

    def test_generate_invoice_filter_partner(self):
        wiz = self.env['invoice.activities.wizard'].create({})
        wiz.partner_ids = [(6, 0, [self.partners[0].id])]
        res = wiz.with_context(open_invoices=True).create_invoices()
        self.assertNotEqual(res.get('res_ids'), [], 'failed to generate invoice when filter partner')


    def test_generate_invoice_option_groupby_project(self):
        wiz = self.env['invoice.activities.wizard'].create({})
        wiz.groupby_project = True
        res = wiz.with_context(open_invoices=True).create_invoices()
        # invoices = self.env['account.move'].browse(res.get('res_ids'))
        # total = 0
        # for inv in invoices:
        #     total += inv.amount_total
        self.assertEqual(len(res.get('res_ids')), 2, 'invoice is not groupped correctly')
    
    def test_generate_invoice_option_groupby_partner(self):
        wiz = self.env['invoice.activities.wizard'].create({})
        wiz.groupby_partner = True
        res = wiz.with_context(open_invoices=True).create_invoices()
        self.assertEqual(len(res.get('res_ids')), 1, 'invoice is not groupped correctly')

    def test_generate_invoice_option_desc(self):
        wiz = self.env['invoice.activities.wizard'].create({})
        wiz.add_timesheet_desc = True
        res = wiz.with_context(open_invoices=True).create_invoices()
        invoices = self.env['account.move'].browse(res.get('res_ids'))
        exist = True
        for inv in invoices:
            line = inv.invoice_line_ids[0]
            if "description : " not in line.name:
                exist = False
        self.assertEqual(exist, True, 'invoice option description not working')

    def test_generate_invoice_option_date(self):
        wiz = self.env['invoice.activities.wizard'].create({})
        wiz.add_timesheet_date = True
        res = wiz.with_context(open_invoices=True).create_invoices()
        invoices = self.env['account.move'].browse(res.get('res_ids'))
        exist = True
        for inv in invoices:
            line = inv.invoice_line_ids[0]
            if "date : " not in line.name:
                exist = False
        self.assertEqual(exist, True, 'invoice option date not working')
