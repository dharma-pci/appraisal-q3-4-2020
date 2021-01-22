from odoo import api, fields, models

class Website(models.Model):
    _inherit = 'delivery.carrier'

    route_id = fields.Many2one('stock.location.route', 'Route')