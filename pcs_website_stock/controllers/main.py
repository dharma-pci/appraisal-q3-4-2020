from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website


class WebsiteSaleStock(WebsiteSale):

    @http.route(['/shop/warehouse/<int:wh_id>'], type='http', auth="public", website=True, sitemap=False)
    def switch_warehouse(self, wh_id, **post):
        """
        to set variable current_warehouse in session based on customer selected one of the warehouses (Shop)
        """
        warehouse_id = request.env['stock.warehouse'].sudo().browse(wh_id)
        request.session['current_warehouse'] = warehouse_id.id
        return request.redirect(request.httprequest.referrer or '/shop')
    
    @http.route(['/shop/warehouses/'], type='http', auth="public", website=True, sitemap=False)
    def remove_current_warehouse(self, **post):
        """
        set to False variable current_warehouse in session based on customer selected all warehouse (Shop)
        """
        request.session['current_warehouse'] = False
        return request.redirect(request.httprequest.referrer or '/shop')

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
        inherit this function to 
        set and displaying quantity on hand product based on session current_warehouse (Shop)
        """
        response = super(WebsiteSaleStock, self).shop(page, category, search, ppg, **post)
        bins = response.qcontext.get('bins',[])
        wh_id = request.env['stock.warehouse'].sudo().browse(request.session.get('current_warehouse',False))
        obj_quant = request.env['stock.quant'].sudo()
        for bin in bins:
            for b in bin:
                product = b['product'].sudo()
                if not wh_id:
                    stock_quant = obj_quant.search([('product_id','=',b['product'].id),('on_hand','=',True)])
                    qoh = sum(quant.quantity - quant.reserved_quantity for quant in stock_quant)
                else:
                    qoh = obj_quant._get_available_quantity(product, wh_id.lot_stock_id)
                b['qoh'] = qoh
        return response


class WebsiteWarehouse(Website):

    @http.route()
    def toggle_switchable_view(self, view_key):
        """
        inherit this function to
        display or hide quantity on hand product when user switching on/off toggle stock availability,
        if toggle off then remove session current_warehouse too
        """
        super(WebsiteWarehouse, self).toggle_switchable_view(view_key)
        if view_key == 'pcs_website_stock.products_website_stock':
            view_products = request.website.viewref('pcs_website_stock.products_website_stock')
            request.website.viewref('pcs_website_stock.products_item_website_stock').active = view_products.active
            if view_products and not view_products.active:
                request.session.pop('current_warehouse', None)
