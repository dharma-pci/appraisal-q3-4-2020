# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'PCS - Pos Discount Authentication',
    'version': '13.0.0.1',
    'author': 'Port Cities',
    'website': 'https://www.portcities.net',
    'summary': 'Custom of Pos Order Return',
    'description': """
        Version 0.0.1: \n
            By Hajiyanto P \n
            This module the purpose to Authentication Discount for POS USER
    """,
    'category': 'Point Of Sale',
    'images': [],
    'depends': ['point_of_sale'],
    'data': [
        'views/point_of_sale_template.xml',
        'views/pos_order_views.xml',
        'views/res_users_views.xml',
    ],
    'qweb': [  
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
