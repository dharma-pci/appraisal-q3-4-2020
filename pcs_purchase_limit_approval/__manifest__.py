# -*- coding: utf-8 -*-
{
    'name': "PCS - Purchase Limit Approval",
    'author': "Portcities",
    'website': "http://www.portcities.net",
    'category': 'purchase',
    'version': '13.0.1.0',
    'summary': """
        Custom Purchase limit approval
       """,
    'description': """
        v1.0
        *Custom Purchase limit approval
        - Add activiy Schedule to Purchase manager if Order exceed the minimum amount for approval
           """,
    'depends': ['purchase'],
    'data': [
        'data/activity_data.xml',
        'view/res_users_view.xml',
        'view/purchase_order_view.xml',
    ],
}
