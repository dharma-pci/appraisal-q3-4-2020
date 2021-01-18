{
    'name': 'Sales Multi Pricelist',
    'version': '13.1.0.0',
    'depends': ['sale_management'],
    'author': 'PortCities Ltd',
    'category': 'Sales',
    'summary': 'Multiple Sale Order Pricelist',
    'description': """
        this module contains customization multiple pricelist in sale order
    """,
    'data': [
        'views/sale_order_view.xml',
        'wizard/pricelist_selection_view.xml'
    ],
    'website': 'https://erp.portcities.net/',
    'installable': True,
    'auto_install': False,
    'application': False,
}
