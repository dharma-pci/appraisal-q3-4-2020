from odoo import models, fields, api, _
from datetime import date, timedelta

class SalesTarget(models.Model):
    _name = 'sales.target'

    name = fields.Char(string='Name',default='New',readonly=True)
    salesperson_id = fields.Many2one('res.users', string='Salesperson',required=True)
    start_date = fields.Date(string='Start Date',required=True)
    end_date = fields.Date(string='End Date',required=True)
    target = fields.Float(compute='_compute_target', string='Target',store=True)
    achieve = fields.Float(compute='_compute_achieve', string='Achieve',store=True)
    achieve_percentage = fields.Float(compute='_compute_achieve_percentage', string='Achieve Percentage',store=True)
    line_ids = fields.One2many('sales.target.line', 'sales_target_id', string='Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled'),
    ], string='Status',default='draft')

    @api.model
    def create(self, vals):
        """ Set name with sequence seq.sales.target """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('seq.sales.target')
        result = super(SalesTarget, self).create(vals)
        return result
    
    @api.depends('line_ids.target')
    def _compute_target(self):
        """ Calculate target from line_ids """
        for rec in self:
            res = 0.0
            if rec.line_ids:
                res = sum([x.target for x in rec.line_ids])
            rec.target = res

    @api.depends('line_ids.achieve_quantity')
    def _compute_achieve(self):
        """ Calculate achieve_quantity from line_ids """
        for rec in self:
            res = 0.0
            if rec.line_ids:
                res = sum([x.achieve_quantity for x in rec.line_ids])
            rec.achieve = res

    @api.depends('line_ids.achieve_percentage')
    def _compute_achieve_percentage(self):
        """ Calculate achieve_percentage from line_ids """
        for rec in self:
            res = 0.0
            if rec.line_ids:
                res = sum([x.achieve_percentage for x in rec.line_ids]) / len(rec.line_ids)
            rec.achieve_percentage = res

    def btn_open(self):
        """ Update state to open """
        self.write({'state':'open'})

    def btn_closed(self):
        """ Update state to closed """
        self.write({'state':'closed'})

    def btn_cancel(self):
        """ Update state to cancel """
        self.write({'state':'cancel'})

    def _body_html(self,target_id):
        """ Template mail sending weekly
            :param record target_id: will be used as the reference of the sale order target
        """
        html = _("""
            <b>Helo <br/>
            This is your Target Details, <br/> <br/></b>

            Salesperson : %s <br/>
            Start Date : %s <br/>
            End Date : %s <br/>
            Target Achieve : %s <br/> <br/>

            Total Target :  %s<br/>
            Total Achieve : %s <br/>
            Achieve percentage : %s &#37;<br/><br/>

            <b>Target Details</b><br/>
            <table class="table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Target Quantity</th>
                        <th>Achieve Quantity</th>
                        <th>Achieve Percentage</th>
                    </tr>
                </thead>
        """) % (target_id.salesperson_id.display_name, 
                target_id.start_date, 
                target_id.end_date, 
                target_id.name, 
                target_id.target, 
                target_id.achieve, 
                target_id.achieve_percentage,
                )
        for line in target_id.line_ids:
            html += ("""
                <tbody>
                    <tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
                </tbody>
            """) % (line.product_id.display_name, line.target, line.achieve_quantity, line.achieve_percentage)
        
        html+= """</table>"""

        return html
        
    def schedule_mail_sales_target(self):
        """ This function is create mail.mail record to sending mail for each sales based on sales target with state open and
            between start and end date.
        """
        today = date.today()
        target_ids = self.env['sales.target'].search([('state','=','open'),('start_date','<=',today),('end_date','>=',today)])
        for rec in target_ids:
            mail_values = {
                'email_from': self.env.company.email,
                'recipient_ids': rec.salesperson_id.partner_id,
                'subject': "Sales Target Email",
                'author_id': 3
                }
            body_html = self._body_html(rec)
            self.env['mail.mail'].create(dict(body_html=body_html, state='outgoing', **mail_values))



class SalesTargetLine(models.Model):
    _name = 'sales.target.line'

    sales_target_id = fields.Many2one('sales.target', string='Sales Target')
    product_id = fields.Many2one('product.product', string='Products')
    target = fields.Float(string='Target Quantity')
    achieve_quantity = fields.Float(string='Achieve Quantity')
    achieve_percentage = fields.Float(string='Achieve Percentage')
    order_line_ids = fields.Many2many('sale.order.line', compute='get_order_lines', string='Order Lines')

    def get_order_lines(self):
        """ This function is fetch sale order line data based on product, state is sale, salesperson and sale order date is between start and end date.
            Then the quantity ordered from data will counting into achieve quantity.
        """
        for rec in self:
            res = False
            if rec.sales_target_id.state == 'open':
                order_lines = self.env['sale.order.line'].search([('state','=','sale'),('product_id','=',rec.product_id.id),('order_id.date_order','>=',rec.sales_target_id.start_date),('order_id.date_order','<=',rec.sales_target_id.end_date),('order_id.user_id','=',rec.sales_target_id.salesperson_id.id)])
                if order_lines:
                    res = order_lines
                result_achieve_quantity = 0.0
                result_achieve_percentage = 0.0
                if order_lines and rec.target > 0:
                    result_achieve_quantity = sum([x.product_uom_qty for x in order_lines])
                    if result_achieve_quantity > 0:
                        result_achieve_percentage =(result_achieve_quantity / rec.target) * 100
                rec.achieve_quantity = result_achieve_quantity
                rec.achieve_percentage = result_achieve_percentage
            rec.order_line_ids = res