from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import UserError


class WebsiteSaleDelivery(WebsiteSale):
    
    @http.route(['/shop/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        res = super(WebsiteSaleDelivery, self).update_eshop_carrier(**post)
        order = request.website.sale_get_order()
        carrier = request.env['delivery.carrier'].search([('id','=',post.get('carrier_id'))])
        if carrier.route_id :
            for line in order.order_line:
                line.update({
                    'route_id':carrier.route_id.id
                })
        return res
