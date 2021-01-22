from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    allow_invoice = fields.Boolean('Allow Timesheet Invoicing')