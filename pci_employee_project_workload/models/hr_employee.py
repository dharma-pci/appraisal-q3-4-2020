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

        for company_id in company_ids:
            filtered_employee_ids = employee_ids.filtered(lambda r: r.company_id == company_id)
            if not filtered_employee_ids:
                continue

            days_workload = company_id.days_workload
            min_workload_hours = company_id.min_workload_hours

            if not days_workload or not min_workload_hours:
                _logger.error(f"Can't process calculation workload for company: {company_id.display_name}. Configuration has not beed set properly.")
                continue

            start_days = fields.Date.today() + timedelta(days=1)
            end_days = fields.Date.today() + timedelta(days=days_workload)
            task_ids = self.env['project.task'].search([('kanban_state', '!=', 'blocked'),
                                                        ('date_deadline', '>=', start_days),
                                                        ('date_deadline', '<=', end_days),
                                                        ('user_id', '!=', False),
                                                        ('remaining_hours', '>', 0),
                                                        ('company_id', '=', company_id.id)])

            for employee_id in filtered_employee_ids:
                user_id = employee_id.user_id
                filtered_task_ids = task_ids.filtered(lambda r: r.user_id == user_id)
                total_remaining_hours = sum(filtered_task_ids.mapped('remaining_hours')) if filtered_task_ids else 0.0
                employee_id.update({
                    'next_workload_total': total_remaining_hours,
                    'is_overload': total_remaining_hours > min_workload_hours,
                })
