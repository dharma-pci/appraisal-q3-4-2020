# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class SplitInvoice(models.TransientModel):
    _name = 'split.invoice'

    split_line_ids = fields.One2many('split.invoice.line', 'split_id', string="Split Line")
    split_selection = fields.Selection([('full','Full Invoice'),('invoice_line','Invoice Line')], default='full', string="Split Selection")
    partner_id = fields.Many2one('res.partner', string="Customer/Supplier")
    percentage = fields.Integer(string="Percentage to Split")
    split_by = fields.Selection([('qty','Quantity')], string="Split Line by")

    @api.model
    def default_get(self, fields_list):
        res = super(SplitInvoice, self).default_get(fields_list)
        invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
        split_line = []
        res['partner_id'] = invoice_id.partner_id.id
        for line in invoice_id.invoice_line_ids:
            split_line.append(((0, 0, {'inv_line_id': line.id,
                                        'product_id': line.product_id.id,
                                        'description': line.name,
                                        'quantity': line.quantity,
                                        'price_unit': line.price_unit
                                    })))
        res['split_line_ids'] = split_line
        return res

    def remove_line(self, invoice_id, invoice_split_id):
        for line in invoice_id.invoice_line_ids:
            line.with_context(check_move_validity=False).unlink()

        for line in invoice_split_id.invoice_line_ids:
            line.with_context(check_move_validity=False).unlink()

    def prepare_line_data(self, product_id, name, qty, price_unit, line_id):
        return {'product_id': product_id.id,
                'name': name,
                'quantity': qty,
                'price_unit': price_unit,
                'sale_line_ids': [(6, 0, line_id.sale_line_ids.ids)],
                'tax_ids': [(6, 0, line_id.tax_ids.ids)],
                }

    def split_invoice(self):
        invoice_line = []
        new_invoice_line = []
        invoice_id = self.env['account.move'].browse(self._context.get('active_id'))
        new_invoice = invoice_id.with_context(check_move_validity=False).copy()
        
        if self.split_selection == 'full':
            for data in self.split_line_ids:
                qty = data.quantity * (self.percentage/100)
                new_qty = data.quantity - (data.quantity * (self.percentage/100))
                line_id = data.inv_line_id
                invoice_line.append(((0,0, self.prepare_line_data(data.product_id, data.description, qty, data.price_unit, line_id))))
                new_invoice_line.append(((0,0, self.prepare_line_data(data.product_id, data.description, new_qty, data.price_unit, line_id))))
            
        elif self.split_selection == 'invoice_line':
            if self.split_by == 'qty':
                for data in self.split_line_ids:
                    qty = data.split_qty
                    new_qty = data.quantity - qty
                    line_id = data.inv_line_id
                    invoice_line.append(((0,0, self.prepare_line_data(data.product_id, data.description, qty, data.price_unit, line_id))))
                    new_invoice_line.append(((0,0, self.prepare_line_data(data.product_id, data.description, new_qty, data.price_unit, line_id))))
        
        self.remove_line(invoice_id, new_invoice)
        invoice_id.with_context(check_move_validity=False).write({'invoice_line_ids': invoice_line})
        new_invoice.with_context(check_move_validity=False).write({'invoice_line_ids': new_invoice_line})


class SplitInvoiceLine(models.TransientModel):
    _name = 'split.invoice.line'

    product_id = fields.Many2one('product.product', string="Product")
    description = fields.Char(string="Description")
    quantity = fields.Float()
    split_qty = fields.Float(string="Split QTY")
    inv_line_id = fields.Many2one('account.move.line', string="Invoice Line")
    split_id = fields.Many2one('split.invoice')
    price_unit = fields.Float()
