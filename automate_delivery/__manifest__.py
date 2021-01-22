{
    'name': "Automate Delivery by Product Owner",
    'version': '13.0.1.0.0',
    'author': "Muhammad Fitrohudin",
    'category': 'Sales',
    'website': 'https://www.portcities.net',
    'description': """
    Feature Automate Delivery by Product Owner
    """,
    'depends': [
        'sale', 'sale_stock'
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/stock_move_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
