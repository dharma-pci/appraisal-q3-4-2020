# pylint: disable=C0111,W0104
# -- coding: utf-8 --
{
    'name': 'PCS - Pricelist Restriction',
    'version': '13.0.1.0.0',
    'summary': 'PCS - Pricelist Restriction',
    'description': """
        Restrict Pricelist According User/Partner Configuration
    """,
    'category': 'sale',
    'author': "Portcities Ltd",
    'website': "http://www.portcities.net",
    'depends': ['sale_management'],
    'data': ['views/partner_view.xml',
             'views/users_view.xml',
             'views/product_pricelist_view.xml',
             'views/res_config_settings_view.xml',
             'views/sale_order_view.xml',
             'wizard/assign_pricelist_wizard_view.xml'],
    'installable': True,
    'application': False,
    'auto_install': False
}
