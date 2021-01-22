# -*- coding: utf-8 -*-
{
    'name': 'PCI Portal User Invoice', 
    'version': '13.0.0.1',
    'category': 'Portal',
    'summary': 'Custom of Portal to confirm Invoice',
    'description': """
        Version 0.0.1: \n
            This module for modification Portal to create button confirm invoice
    """,
    'website': 'https://www.portcities.net',
    'author':'Portcities Ltd.',
    'images': [],
    'depends': ['account'],
    'data': [
        'views/portal_invoice.xml',
    ],
    'qweb': [  
        'static/src/xml/*.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}