# pylint: disable=C0111,W0104
# -- coding: utf-8 --
{
    'name': 'Portcities - Delivery Options',
    'version': '13.0.1.0.0',
    'summary': 'Add 2 step routes in shipping method pickup in store and delivered',
    'description': """
        Add 2 step routes in shipping method pickup in store and delivered
    """,
    'category': 'eCommerce',
    'author': "Portcities Ltd",
    'website': "http://www.portcities.net",
    'depends': ['website_sale_delivery'],
    'data': [
        'views/delivery_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
