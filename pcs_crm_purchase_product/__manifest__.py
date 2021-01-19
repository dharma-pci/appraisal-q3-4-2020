{
    'name': 'Purchase Products from CRM',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'CRM/Purchase',
    'description': """
        Add product lines which are going to be added on CRM which further generates requests for quotation to multiple vendors.
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'images': [],
    'depends': ['crm', 'stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/product_views.xml'
    ],
    'active': True,
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
