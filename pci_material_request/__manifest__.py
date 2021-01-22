{
    'name': 'Material Request',
    'version': '13.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Material Request',
    'website': 'https://www.portcities.net',
    'author':'Portcities Ltd.',
    'images': [],
    'depends': [
        'mrp_workorder',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/material_request_data.xml',
        'views/material_request_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
