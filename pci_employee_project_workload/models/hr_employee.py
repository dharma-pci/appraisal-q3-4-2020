import logging
from datetime import timedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    next_workload_total = fields.Float(string=_('Next Period Workload Total'))
    is_overload = fields.Boolean(string=_('Next Period Work Overload'))
    company_min_workload_hours = fields.Float(related='company_id.min_workload_hours')
    company_days_workload = fields.Integer(related='company_id.days_workload')

    @api.model
    def cron_calculate_workload(self):
        """ Calculate employee workload in next period.
            Called from scheduler.
        """
        company_ids = self.env['res.company'].search([])
        employee_ids = self.search([('company_id', 'in', company_ids.ids),
                                    ('user_id', '!=', False)])

        ctx_user_id = self.env.user.id
        datetime_now = fields.Datetime.to_string(fields.Datetime.now())

        for company_id in company_ids:
            filtered_employee_ids = employee_ids.filtered(lambda r: r.company_id == company_id)
            if not filtered_employee_ids:
                continue

            days_workload = company_id.days_workload
            min_workload_hours = company_id.min_workload_hours

            if not days_workload or not min_workload_hours:
                _logger.error(f"Can't process calculation workload for company: {company_id.display_name}. Configuration has not beed set properly.")
                continue

            start_days = fields.Date.to_string(fields.Date.today() + timedelta(days=1))
            end_days = fields.Date.to_string(fields.Date.today() + timedelta(days=days_workload))

            employee_user_ids = filtered_employee_ids.mapped('user_id')
            sql = """SELECT user_id,
                            SUM(remaining_hours) AS total_remaining_hours
                     FROM project_task
                     WHERE user_id IN %s
                           AND kanban_state != 'blocked'
                           AND date_deadline BETWEEN %s AND %s
                           AND remaining_hours > 0
                           AND company_id = %s
                     GROUP BY user_id"""
            self._cr.execute(sql, (tuple(employee_user_ids.ids), start_days, end_days, company_id.id,))
            fetch = self._cr.fetchall()
            map_user_hours = dict((x, y) for x, y in fetch)

            for employee_id in filtered_employee_ids:
                user_id = employee_id.user_id
                total_remaining_hours = map_user_hours.get(user_id.id, 0)
                is_overload = total_remaining_hours > min_workload_hours
                sql_update = """UPDATE hr_employee
                                SET next_workload_total = %s, is_overload = %s, write_uid = %s, write_date = %s
                                WHERE id = %s"""

                params = (total_remaining_hours, is_overload, ctx_user_id, datetime_now, employee_id.id,)
                self._cr.execute(sql_update, params)
