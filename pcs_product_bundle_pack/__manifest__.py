{
    'name': 'PCS - Product Pack/Bundle',
    'version': '13.0.1.0.0',
    'author': 'Portcities Ltd',
    'category': 'Inventory',
    'description': """
            Product bundle Pack is offering several products for sale as one combined product which you can able to sell 
            as combo product kit easily from sales order and able to deliver all products pack of kit in delivery orders.
    """,
    'depends': [
        'stock',
        'product',
        'sale',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pack_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
}
