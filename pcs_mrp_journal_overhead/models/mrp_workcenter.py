# import odoo
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MrpWorkcenter(models.Model):
    """ inherit model mrp.workcenter """

    _inherit = 'mrp.workcenter'

    # Fields declaration
    overhead_account = fields.Many2one('account.account', string="Overhead Account")
    