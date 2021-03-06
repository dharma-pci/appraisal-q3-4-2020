{
    'name': "PCI Employee Project Workload",
    'summary': """Calculate employee project workload for PCI""",
    'description': """
- Calculate employee workload for next period, based on project task
    """,
    'author': "Port Cities",
    'website': "https://portcities.com",
    'category': 'Services/Timesheets',
    'version': '14.0.1',
    'depends': ['hr_timesheet'],
    'data': [
        'data/ir_cron_data.xml',
        'views/res_company_views.xml',
        'views/hr_employee_views.xml',
    ],
}
