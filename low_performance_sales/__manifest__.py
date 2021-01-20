# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Low Performance Sales Report',
    'version': '13.0.1.0.0',
    'sequence': 1,
    'category': 'Sales',
    'summary': 'Show products which have poor sales performance',
    'description': """
        Show products which have poor sales performance in Odoo pivot table or Excel file
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'images': [],
    'depends': ['sale', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'report/low_performance_sale_views.xml',
        'views/sale_views.xml',
        'wizard/low_perform_options_views.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
