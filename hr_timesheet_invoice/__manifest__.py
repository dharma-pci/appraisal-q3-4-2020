{
    'name': 'Timesheet Invoice',
    'version': '1.0',
    'description': 'Create invoice from timesheet',
    'summary': 'Create invoice from timesheet',
    'author': 'Portcities, Ltd',
    'website': 'https://portcities.net',
    'category': 'Operations/Timesheets',
    'depends': [
        'hr_timesheet',
        'account',
    ],
    'data': [
        'views/project_project_views.xml',
        'views/account_analytic_line_views.xml',
        'wizard/invoice_activities_wizard_views.xml',
    ],
    'auto_install': True,
    'application': True,
}