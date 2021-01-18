from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    min_workload_hours = fields.Float(string=_('Minimum Workload Hours'))
    days_workload = fields.Integer(string=_('Set Days to Calculate Workload'))
