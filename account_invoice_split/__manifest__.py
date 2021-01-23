{
    'name': 'Appraisal Q3-4 2020',
    'version': '13.0.1.0.0',
    'summary': 'Split Invoice',
    'description': """
        Split Invoice
    """,
    'category': 'Invoice',
    'author': "Portcities Ltd",
    'website': "http://www.portcities.net",
    'depends': ['sale', 'account', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        'views/sale_view.xml',
        # 'wizard/mrp_mps_forecast_details_views.xml',
            ],
    'qweb':[],
    'installable': True,
    'application': False,
    'auto_install': False
}
