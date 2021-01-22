# -*- coding: utf-8 -*-
{
    'name': 'Pos Order Return',
    'version': '13.0.0.1',
    'category': 'Point Of Sale',
    'summary': 'Custom of Pos Order Return',
    'description': """
        Version 0.0.1: \n
            By Andrew.Y.K \n
            This module for modification Pos to make return in pos screen
    """,
    'website': 'https://www.portcities.net',
    'author':'Portcities Ltd.',
    'images': [],
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
        'views/js_template.xml',
    ],
    'qweb': [  
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
