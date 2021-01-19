from odoo import models,fields,api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approver_id = fields.Many2one('res.users',readonly=True,string="Approved By")

    def button_confirm(self):
        """override this button in order to add activity scheduler"""
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                mail_obj = self.env['mail.activity']
                in_charge_id = self.env.user.purchase_leader_id
                
                if not in_charge_id:
                    raise UserError("Please set Purchase Leader for current user in Users Setting.")

                value = {
                    'activity_type_id' : self.env.ref('pcs_purchase_limit_approval.mail_activity_data_reminder').id,
                    'summary' : "Approval of %s"%(order.name),
                    'date_deadline' : order.date_order.date(),
                    'user_id' : in_charge_id.id,
                    'res_model' : order._name,
                    'res_model_id' : self.env.ref('purchase.model_purchase_order').id,
                    'res_id' : order.id
                }
                mail_obj.sudo().create(value)
                order.write({'state': 'to approve'})
        return True
    
    def button_approve(self):
        res = super(PurchaseOrder,self).button_approve()
        self.write({'approver_id':self.env.user.id})
        return res
