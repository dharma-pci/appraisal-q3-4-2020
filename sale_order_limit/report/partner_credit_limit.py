from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class PartnerCreditLimitReport(models.Model):
    _name = 'partner.credit.limit'
    _description = "Partner Credit Limit"

    partner_id = fields.Many2one(
        'res.partner', 
        readonly=True)
    currency_id = fields.Many2one(
        'res.currency', 
        default=lambda self:self.env.user.company_id.currency_id.id)
    credit = fields.Monetary(readonly=True)
    unpaid_amount = fields.Monetary(readonly=True)
    # exceeded_credit = fields.Monetary(readonly=True)
    remaining_credit = fields.Monetary(readonly=True)

    currency_id = fields.Many2one('res.currency', 
        readonly=True, 
        compute="_compute_currency_id", 
        default=lambda self:self.env.user.company_id.currency_id)

    _auto = False

    @api.model
    def find_partner(self, partners, low_level=None):
        if not low_level:
            return self.search([('partner_id','in',partners.ids)])
        else:
            self.env.cr.execute("""SELECT * FROM partner_credit_limit WHERE partner_id in %s""", (tuple(partners.ids),))
            return self.env.cr.dictfetchall()

    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = self.env.user.company_id.currency_id.id
    

    def query_so_uninvoice(self):
        query  = """
            SELECT 
                sr.partner_id,SUM(
                    price_total
                ) AS subtotal
            FROM sale_report AS sr
            WHERE sr.invoice_status not in ('invoiced') and state not in ('draft','cancel','sent')
            GROUP BY sr.partner_id
        """
        return query

    def query_unpaid_invoices(self):
        query  = """
            SELECT partner_id, SUM(amount_residual) as subtotal
            FROM 
                account_move
            WHERE journal_id = (select id from account_journal where type='sale' limit 1)
                   AND state not in ('cancel')
                   AND payment_state in ('not_paid', 'partial')
            GROUP BY partner_id
        """
        return query
    

    def query(self):
        query = """
            WITH sale_uninvoice AS (
                %s
            ), unpaid_invoices AS (
                %s
            )
            SELECT
                rp.id 
                ,rp.id as partner_id
                ,rp.credit_limit as credit
                ,(
                    (CASE WHEN s.subtotal IS NOT NULL then s.subtotal else 0 END) + 
                    (CASE WHEN i.subtotal IS NOT NULL THEN i.subtotal ELSE 0.0 END)
                ) AS unpaid_amount
                ,(
                    (CASE WHEN rp.credit_limit IS NOT NULL THEN rp.credit_limit ELSE 0 END) -  
                    (
                        (CASE WHEN s.subtotal IS NOT NULL then s.subtotal else 0 END) + 
                        (CASE WHEN i.subtotal IS NOT NULL THEN i.subtotal ELSE 0.0 END)
                    )
                ) AS remaining_credit
            FROM res_partner AS rp
            LEFT JOIN sale_uninvoice AS s ON s.partner_id = rp.id
            LEFT JOIN unpaid_invoices AS i ON i.partner_id = rp.id
        """ % (self.query_so_uninvoice(), self.query_unpaid_invoices(),)

        return query
    
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )""" % (self._table, self.query(), ))