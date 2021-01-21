import odoo

from odoo import api, fields, models

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    personal_pickup = fields.Boolean()
    message_alert = fields.Char(string='Warning Message' , translate=True , help="Warning when not available stock in location")