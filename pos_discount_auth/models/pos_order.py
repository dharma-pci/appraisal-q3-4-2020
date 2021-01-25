# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class PosOrderLine(models.Model):
	""" Inerit POS Order Line to adding information of Manager Approval disocunt"""
	_inherit = 'pos.order.line'

	manager_disc_approval = fields.Many2one('res.users', string="Manager Disc Approval")