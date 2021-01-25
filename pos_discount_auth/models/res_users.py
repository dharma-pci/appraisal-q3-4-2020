# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ResUsers(models.Model):
	""" Inherit Res Users"""
	_inherit = 'res.users'

	pin = fields.Char('PIN', help="set PIN to set on POS.")


	@api.model
	def check_authentication(self, user, password):
		# Function to check Authentication manager from POS UI
		login_status = "Success"
		manager_id = self.browse(user)
		vals = {"login_status":login_status}
		if manager_id.pin:
			if manager_id.pin == password:
				return vals
			else:
				vals['login_status'] = "Wrong Password"
				return vals
		else:
			vals['login_status'] = "PIN is not yet Created, Plese Input First!!"
			return vals