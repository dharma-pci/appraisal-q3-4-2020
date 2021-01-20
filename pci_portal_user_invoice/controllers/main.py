# -*- coding: utf-8 -*-

import logging
import re

from collections import OrderedDict
from werkzeug.urls import url_encode

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/my/invoice/confirm_post/<int:invoice_id>'], type='http', auth="user", website=True)
    def my_invoice_confirm_post(self, invoice_id, access_token=None, **kw):        
        try:
           self._document_check_access('account.move', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        invoice = request.env['account.move'].sudo().browse(invoice_id)
        invoice.action_post()
        return request.redirect('/my/invoices/'+ str(invoice_id))