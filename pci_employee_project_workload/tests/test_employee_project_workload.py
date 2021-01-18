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
