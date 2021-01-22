
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Appraisal - Sale Order Automation",
    "author": "Portcities",
    "version": "13.0.1.0.0",
    "summary": "Sale Order Automation",
    "description" : """
                This module auto Create Picking and Invoice or auto validate when confirm sale order. \n
                    - Author : Fadhil <fadhil@portcities.net>
    """,
    "category": "Sale",
    "depends": ["sale_stock"],
    "data": [
        "views/stock_warehouse_views.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
    
    
}
