# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inventory - Merged Picking',
    'version': '13.0.1.0.0',
    'category': 'Merged Picking',
    'summary': 'Merged Picking DO/Receipt',
    'description': """
            Author : Yohanes
    """,
    'website': 'https://www.portcities.net',
    'author':'Portcities Ltd.',
    'images': [],
    'depends': ['stock','sale_stock','sale_management','purchase_stock'],
    'data': [
        'views/sale_order_view.xml',
        # 'views/purchase_order_view.xml',
        'wizard/merge_picking_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}