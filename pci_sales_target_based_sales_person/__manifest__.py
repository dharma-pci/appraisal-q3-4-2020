{
    'name': 'PCI Sales Target Based Salesperson',
    'summary': """
        PCI Sales Target Based Salesperson""",
    'version': '13.0.1',
    'category': '',
    'author': 'Portcities Ltd',
    'description': """
        author : Rp. Bimantara \n
        Custom module = PCI Sales Target Based Salesperson
    """,
    'depends': [
        'sale',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'views/sales_target_views.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True    
}