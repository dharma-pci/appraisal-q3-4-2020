import time
from datetime import timedelta

from odoo import fields
from odoo.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet


class TestEmployeeProjectWorkload(TestCommonTimesheet):
    def setUp(self):
        """ Inherit setUp() and set default value for company """
        super().setUp()
        company_ids = self.env['res.company'].search([])
        self.company_id = company_ids[0]
        self.company_id.write({
            'min_workload_hours': 40,
            'days_workload': 7,
        })

    def test_employee_work_overload(self):
        """ Test with result employee is overload """
        self.user_employee.company_id = self.company_id
        self.task1.write({
            'kanban_state': 'normal',
            'user_id': self.user_employee.id,
            'date_deadline': fields.Date.today() + timedelta(days=2),
            'planned_hours': 50,
        })

        # this task deadline is expired, so this should not be calculated
        self.task2.write({
            'kanban_state': 'normal',
            'user_id': self.user_employee.id,
            'date_deadline': fields.Date.today() - timedelta(days=1),
            'planned_hours': 10,
        })

        self.env['hr.employee'].cron_calculate_workload()
        self.assertEqual(self.empl_employee.next_workload_total, 50)
        self.assertTrue(self.empl_employee.is_overload)

    def test_employee_work_not_overload(self):
        """ Test with result employee is not overload """
        self.user_employee2.company_id = self.company_id
        self.task1.write({
            'user_id': self.user_employee2.id,
            'date_deadline': fields.Date.today() + timedelta(days=2),
            'planned_hours': 20,
        })

        # this task deadline is expired, so this should not be calculated
        self.task2.write({
            'user_id': self.user_employee2.id,
            'date_deadline': fields.Date.today() - timedelta(days=1),
            'planned_hours': 30,
        })

        self.env['hr.employee'].cron_calculate_workload()
        self.assertEqual(self.empl_employee2.next_workload_total, 20)
        self.assertFalse(self.empl_employee2.is_overload)

    def test_many_employee(self):
        for i in range(100):
            idx = i + 1
            user_employee = self.env['res.users'].create({
                'name': f'User Employee {idx}',
                'login': f'user_employee_{idx}',
                'email': f'useremployee_{idx}@test.com',
                'groups_id': [(6, 0, [self.ref('hr_timesheet.group_hr_timesheet_user')])],
            })

            empl_employee = self.env['hr.employee'].create({
                'name': f'User Empl Employee {idx}',
                'user_id': user_employee.id,
            })

            task = self.env['project.task'].create({
                'name': 'Task One',
                'priority': '0',
                'kanban_state': 'normal',
                'project_id': self.project_customer.id,
                'partner_id': self.partner.id,
                'user_id': user_employee.id,
                'date_deadline': fields.Date.today() + timedelta(days=2),
                'planned_hours': 20,
            })

        start_time = time.perf_counter() * 1000
        self.env['hr.employee'].cron_calculate_workload()
        end_time = time.perf_counter() * 1000
        print(f'Result: {(end_time - start_time):0.2f} ms')
