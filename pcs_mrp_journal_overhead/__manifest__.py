{
    "name": "Custom MRP Workorder",
    "summary": "Module Custom to manual input of work order duration",
    "version": "13.0.1.0",
    "author": "Port Cities",
    "website": "https://www.portcities.net",
    "category": "Manufacture",
    "license": "LGPL-3",
    "description": """ 
        Custom module MRP Workorder: by.PC\n
        - Create journal overhead for work orders as cost of production.\n
        - Manual input of work order duration to calculate the overhead cost.\n
        - Balancing journal entries created from manufacturing order.\n

    """,
    "depends": [
        'base',
        'mrp',
        'account',
        'account_asset',
        'mrp_workorder',
        'mrp_account_enterprise'
    ],
    "data": [
        # XML Data
        'data/decimal_precision_data.xml',
        'data/account_account_data.xml',

        # XML Views
        'views/mrp_workcenter_view.xml',
        'views/mrp_workorder_view.xml',
        'views/mrp_production_view.xml',

        # XML Reports
        'reports/cost_structure_report.xml',
    ],
    "demo":[],

    "auto_install": False,
    "installable": True,
    "application": False,
}