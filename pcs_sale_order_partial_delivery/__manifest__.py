# -*- coding: utf-8 -*-

{
    'name': 'Sale Order Partial Delivery',
    'version': '13.0.1.0.0',
    'sequence': 1,
    'category': 'Sale',
    'summary': 'Custom Sale Order module to make Partial Delivery when confirm SO',
    'description': """
        This module contain all Sale Order customizations. \n
        - Authors: AA <albertus@portcities.net>
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'images': [],
    'depends': ['sale','stock'],
    'data': [
        'views/sale_order_form_view.xml',
        'wizard/delivery_order_wizard_form_view.xml',
        'wizard/delivery_order_wizard_line_form_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
