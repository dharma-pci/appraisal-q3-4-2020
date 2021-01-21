import odoo

from odoo import api, fields, http, models

from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/shop/list_warehouse'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def show_all_warehouse(self, **post):
        ''' function to show all available warehouse based on shipping method (Pick up from store)'''
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        personal_pickup=''
        carrier = request.env['delivery.carrier'].sudo().browse(carrier_id)
        if carrier.personal_pickup:
            personal_pickup='True'
            data_warehouse = request.env['stock.warehouse'].sudo().search([('active','=', True)])
            dict_warehouse=[]
            if data_warehouse:
                for warehouse in data_warehouse:
                    dict_warehouse.append({'id':warehouse.id,'name':warehouse.name})
        
        result = self._update_website_sale_delivery_return(order, **post)
        result.update({
            'warehouse_id':dict_warehouse,
        })
        return result

    @http.route(['/shop/check_stock'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def checking_stock_in_warehouse(self, **post):
        ''' function to checking available stock product based on pick up warehouse
            it will check available qty product in warehouse and formula for minimum qty stock
            when stock ready will enable payment button, and when not ready will show alert and disable 
            payment button
            - data for personal_pickup_location will sent to sale.order models
        '''
        order = request.website.sale_get_order()
        value = {}
        ready_to_pick = False
        if post['warehouse_id']:
            warehouse_id = int(post['warehouse_id'])
            carrier_id = int(post['carrier_id'])
            carrier = request.env['delivery.carrier'].sudo().browse(carrier_id)
            personal_pickup = ''
            warehouse_loc = request.env['stock.warehouse'].sudo().search([('id','=', warehouse_id)],limit=1)
            stock_location = warehouse_loc.lot_stock_id.id
            quant = request.env['stock.quant'].sudo()
            storable = 0
            storable_on_stock = 0
            if carrier.personal_pickup:
                personal_pickup='True'
                for line in order.order_line:
                        if line.product_id.type == 'product':
                            storable += 1 
                            qty_available = line.product_id.with_context(location=stock_location).qty_available
                            if qty_available:
                                stck_min = int(line.product_uom_qty)
                                if stck_min <= qty_available:
                                    storable_on_stock += 1
                                ready_to_pick = True
                            else:
                                ready_to_pick = False
                if order:
                    order._check_carrier_quotation(force_carrier_id=carrier_id)
                    result = self._update_website_sale_delivery_return(order, **post)
                    order.update({
                        'personal_pickup_location': warehouse_loc.id,
                    })
                    value.update({
                        'ready_to_pick': ready_to_pick,
                        'message_alert': carrier.message_alert,
                        })
                    return value
            else:
                return value