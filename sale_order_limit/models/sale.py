from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    

    credit_limit = fields.Monetary(compute="_compute_credit_limit")
    unpaid_amount = fields.Monetary(compute="_compute_credit_limit")
    exceeded_amount = fields.Monetary(compute="_compute_credit_limit")

    state = fields.Selection(selection_add=[('sent',),('waiting-approval',"Waiting Approval")])
    unpaid_invoice_ids = fields.One2many("account.move", 
        compute="_compute_credit_limit", 
        string="Pending Invoices")

    form_view_link = fields.Char(string="Form View Link", 
        help="Use for generate link to view a detail to be sent on external", 
        compute="_compute_form_view_link")


    def _compute_form_view_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base = base_url+'/web#id={}&model=sale.order&view_type=form'
        for rec in self:
            rec.form_view_link = base.format(str(rec.id))

    def sales_manager_partner_to(self):
        self.ensure_one()
        manager_group = self.env.ref('sales_team.group_sale_manager')
        partners = manager_group.users.mapped('partner_id')
        return ",".join(map(str,partners.ids))

    def _compute_credit_limit(self):
        partners = self.mapped('partner_id')
        credit_limits = self.env['partner.credit.limit'].search([('partner_id','in',partners.ids)])
        for rec in self:
            
            unpaid_amount = 0.0
            exceeded_amount = 0.0

            pcredit = credit_limits.filtered(lambda r:r.partner_id==rec.partner_id)
            if len(pcredit):
                unpaid_amount = pcredit.unpaid_amount
                exceeded_amount = pcredit.remaining_credit - rec.amount_total
            rec.update({
                'credit_limit':pcredit.credit,
                'unpaid_amount':unpaid_amount,
                'exceeded_amount':exceeded_amount,
                'unpaid_invoice_ids': rec.partner_id.invoice_ids.filtered(lambda r:r.payment_state == False or \
                    r.payment_state not in ('paid','reversed')),
            })

    def request_limit_approval(self):
        self.ensure_one()
        # if user already a manager then force to action_confirm()
        if self.user_has_groups('sales_team.group_sale_manager'):
            self.with_context(approve_limit=1).approve_credit()
            return True
        template = self.env.ref('sale_order_limit.mail_template_sale_order_limit_approval_req')
        if template:
            self.update({'state':'waiting-approval'})

            # if complete then send mail
            self.message_post_with_template(
                            template.id, 
                            composition_mode='comment',
                            model='sale.order', 
                            res_id=self.id,
                            email_layout_xmlid='mail.mail_notification_light',
                        )

        return {'type': 'ir.actions.act_window_close'}
    

    def _approval_credit_validation(self):
        if not self.user_has_groups('sales_team.group_sale_manager'):
            raise UserError(_("You're not authorize to perform this action!"))

        if not self.state in ('waiting-approval') and not self._context.get('approve_limit'):
            raise UserError(_("Fault State to approve credit limit. State should in Waiting Approval!"))

    def approve_credit(self):
        self.ensure_one()
        self._approval_credit_validation()
        res = self.with_context(approve_limit=1).action_confirm()
        if res:
            # mail_template_sale_order_limit_approval_approved
            template = self.env.ref('sale_order_limit.mail_template_sale_order_limit_approval_approved')
            if template:
                self.message_post_with_template(
                            template.id, 
                            composition_mode='comment',
                            model='sale.order', 
                            res_id=self.id,
                            email_layout_xmlid='mail.mail_notification_light',
                        )
            return {'type': 'ir.actions.act_window_close'}

    def _show_credit_limit_wizard(self):
        form = self.env.ref('sale_order_limit.sale_limit_form_view')
        context = dict(self.env.context or {})
        # context.update({}) #uncomment if need append context
        res = {
            'name': "%s - %s" % (_('Limit Exceeded'), self.name),
            'view_type': 'form',# REMOVE IF USING ODOO>=13
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': form.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            'res_id':self.id,
        }
        return res
        

    def check_credit_limit(self):
        """
        check_credit_limit Checking credit limit from partner_credit_limit table then return actions.act_window if limit exceed
        """
        self.ensure_one()
        res = False
        limit = self.env['partner.credit.limit'].search([('partner_id','=',self.partner_id.id)])
        # remaining limit - this order untaxed amount then means the remaining credit not enough
        # then show pop up window
        
        remaining_after_order = limit.remaining_credit - self.amount_untaxed
        if remaining_after_order<0:
            return self._show_credit_limit_wizard()
        else:
            return True


    def action_confirm(self):
        credit_ok = self.check_credit_limit()
        if type(credit_ok)==dict and not self._context.get('approve_limit'):
            # if not in context to approve credit limit
            # if check credit limit return dict actions.act_window
            # then return it
            return credit_ok

        return super().action_confirm()