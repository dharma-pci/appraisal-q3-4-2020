{
	'name': 'PCS - Penalty Invoice',
	'version': '13.0.1.0.0',
	'author': 'Portcities',
	'category': 'Invoicing',
	'license' : 'AGPL-3',
	'description': '''
		
	''',
	'depends': [
		'account',
	],
	'data': [
		'data/penalty_product_data.xml',
		'data/ir_cron_data.xml',
		'views/res_config_settings_views.xml',
		'views/account_move_views.xml',
	],
	'website': 'https://www.portcities.net/',
	'installable': True,
	'auto_install': False,
	'application': False,
}