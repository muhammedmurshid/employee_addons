{
    'name': "Employee Addons",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail', 'hr_holidays','calendar', 'sale', 'hr_expense'],
    'data': [
        # 'security/groups.xml',
        'security/ir.model.access.csv',
        'views/private_number.xml',
        'views/leave_report.xml',
        'views/leave_pivot_view.xml',
        'views/public_time_off_refuse.xml',
        'views/leaves_remove_from_calendar.xml',
        'data/server_action.xml',
        'views/attendance_report.xml'
        # 'views/refuse_public_holiday.xml',
        # 'data/activity.xml',

    ],
    'demo': [],
    'summary': "logic_employee_addons",
    'description': "employee_addons",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
