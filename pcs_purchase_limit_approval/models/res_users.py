from odoo import models,fields,api

class ResUser(models.Model):
    _inherit = 'res.users'

    is_purchase_user = fields.Boolean(compute="_compute_purchase_user")
    is_purchase_manager = fields.Boolean(compute="_compute_purchase_manager")
    purchase_leader_id = fields.Many2one('res.users',domain=lambda self:[('id','in',self.env.ref('purchase.group_purchase_manager').users.ids)])
    purchase_crew_ids = fields.One2many('res.users','purchase_leader_id')

    @api.depends('is_purchase_user')
    def _compute_purchase_user(self):
        for this in self:
            purchase_user_group = self.env.ref('purchase.group_purchase_user')
            if this.id in purchase_user_group.users.ids:
                this.is_purchase_user = True
            else:
                this.is_purchase_user = False
    
    @api.depends('is_purchase_manager')
    def _compute_purchase_manager(self):
        for this in self:
            purchase_manager_group = self.env.ref('purchase.group_purchase_manager')
            if this.id in purchase_manager_group.users.ids:
                this.is_purchase_manager = True
            else:
                this.is_purchase_manager = False