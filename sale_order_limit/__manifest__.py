{
    'name': 'Sale Order Limit',
    'summary': """
        Limit each customer to order. If limit reached then require to approval""",
    'version': '0.0.1',
    'category': 'Sales/Sales',
    'author': 'La Jayuhni Yarsyah @ Portcities',
    'description': """
        Set Credit Limit to each customers. Check every order submited then if limit reached then sales should approve by manager/admin 
    """,
    'depends': [
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/partner.xml',
        'views/sale.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}