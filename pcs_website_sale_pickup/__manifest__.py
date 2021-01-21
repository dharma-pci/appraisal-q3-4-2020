{
    'name': 'Portcities - Website Sale Pick up',
    'version': '13.0.1.0',
    'summary': 'Add warehouse for pick up from store',
    'description': """
        Free shipping method that allow customer to pickup product
    """,
    'category': 'eCommerce',
    'author': "Portcities Ltd",
    'website': "http://www.portcities.net",
    'depends': ['website_sale','portal','website_sale_delivery','delivery'],
    'data': [
        'views/delivery_carrier_view.xml',
        'views/sale_order_view.xml',
        'views/website_sale_delivery_templates.xml',
        'views/website_pickup_assets.xml',
    ],
    'demo': [
        'data/website_pickup_delivery_demo.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
