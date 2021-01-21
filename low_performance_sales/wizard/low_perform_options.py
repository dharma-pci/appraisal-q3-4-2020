# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
from io import BytesIO


class LowPerformOptions(models.TransientModel):
    _name = 'low.perform.options'
    _description = 'Low Perform Options'

    report_type = fields.Selection([('product_variant', 'By Product Variant'),
                                    ('product_template', 'By Product Template')],
                                   string='Report Type', default='product_variant')
    date_from = fields.Date()
    date_to = fields.Date()
    critical_level_qty = fields.Integer('Critical Level (Absolute Quantity)')
    critical_level_currency = fields.Integer('Critical Level (Sales in default currency)')
    product_categ_id = fields.Many2one('product.category', 'Product Category')
    sale_team_ids = fields.Many2many('crm.team', 'crm_low_perform_rel',
                                     'crm_team_id', 'low_id', string='Sales Team')
    country_id = fields.Many2one('res.country', string='Partner Country')
    # SPECIAL FIELDS FOR GENERATING EXCEL
    state_x = fields.Selection([('choose', 'Choose'),
                                ('get', 'Get')], default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.constrains('critical_level_qty', 'critical_level_currency')
    def _check_critical_amount(self):
        for this in self:
            if this.critical_level_qty < 0 or this.critical_level_qty == 0:
                raise UserError(_('Critical Level (Absolute Quantity) '
                                  'Cannot less than zero or equal to zero'))
            if this.critical_level_currency < 0 or this.critical_level_currency == 0:
                raise UserError(_('Critical Level (Sales in default currency) '
                                  'Cannot less than zero or equal to zero'))

    @api.constrains('date_from')
    def _check_date(self):
        for this in self:
            if this.date_from > this.date_to:
                raise UserError(_('Date from cannot be anterior of Date to'))

    def generate_report_odoo(self):
        data = self.get_data()

    def generate_report_excel(self):
        data = self.get_data()
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        filename = 'Low Performance Sale Report.xlsx'

        normal_left = workbook.add_format({'valign': 'vcenter', 'align': 'left'})
        normal_left.set_text_wrap()
        normal_left.set_font_name('Arial Narrow')
        normal_left.set_font_size('12')

        bold_left = workbook.add_format({'valign': 'vcenter', 'align': 'left', 'bold': 1})
        bold_left.set_text_wrap()
        bold_left.set_font_name('Arial Narrow')
        bold_left.set_font_size('12')

        worksheet = workbook.add_worksheet("Low Performance Sales")

        worksheet.write('B2', 'Product', bold_left)
        worksheet.write('C2', 'Qty Sold', bold_left)
        worksheet.write('D2', 'Revenue', bold_left)

        row = 2
        for report_data in data:
            worksheet.write(row, 1, report_data.get('product_name'), normal_left)
            worksheet.write(row, 2, report_data.get('qty_sold'), normal_left)
            worksheet.write(row, 3, report_data.get('revenue'), normal_left)

            row += 1

        workbook.close()
        out = base64.encodebytes(fp.getvalue())
        self.write({
            'data_x': out,
            'state_x': 'get',
            'name': filename
        })

        ir_model_data = self.env['ir.model.data']
        fp.close()
        form_res = ir_model_data.get_object_reference('low_performance_sales',
                                                      'low_perform_options_view_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'low.perform.options',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def get_data(self):
        join = ''
        where = ''
        params = [self.date_from, self.date_to]
        if self.product_categ_id:
            join += ' LEFT JOIN product_category categ ON (categ.id=prod_temp.categ_id)'
            where += ' AND categ.id IN %s'
            params.append(tuple(self.product_categ_id.ids))
        if self.sale_team_ids:
            join += ' LEFT JOIN crm_team crt ON (crt.id=so.team_id)'
            where += ' AND crt.id IN %s'
            params.append(tuple(self.sale_team_ids.ids))
        if self.country_id:
            join += ' LEFT JOIN res_partner partner ON (partner.id=so.partner_id)' \
                    'LEFT JOIN res_country country ON (country.id=partner.country_id)'
            where += ' AND country.id IN %s'
            params.append(tuple(self.country_id.ids))
        cr = self.env.cr
        sql = """
            SELECT prod_temp.name as product_name, sum(sol.product_uom_qty) as qty_sold, 
                sum(sol.price_subtotal) as revenue, prod.id as product_id, 
                prod_temp.id as product_tmpl_id
            FROM sale_order_line sol
            LEFT JOIN sale_order so ON (so.id=sol.order_id)
            LEFT JOIN product_product prod ON (prod.id=sol.product_id)
            LEFT JOIN product_template prod_temp ON (prod_temp.id=prod.product_tmpl_id)""" \
              + join + """
            WHERE so.date_order BETWEEN %s AND %s """ + where + """
            GROUP BY prod_temp.name, prod.id, prod_temp.id
        """
        cr.execute(sql, tuple(params))

        return cr.dictfetchall()

    def variant_or_template(self, report_type):
        """
        static function to determine which object will be used
        :param report_type: type of report desired by the user
        :return: object name
        """
        if report_type == 'product_variant':
            return 'product.product'
        else:
            return 'product.template'
