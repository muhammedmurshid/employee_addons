from odoo import models, fields, api
from datetime import datetime


class LeaveReportPivotCustom(models.Model):
    _name = 'leave.report.pivot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Leave Report Pivot'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    leave_type = fields.Char(string='Leave Type')
    taken_leaves = fields.Float(string='Taken Leaves')
    remaining_leaves = fields.Float(string='Remaining Leaves')
    max_leaves = fields.Float(string='Max Leaves')

    def action_duplicate_accounts(self):

        current_year = datetime.now().year
        print(current_year, 'yearlo')
        employees = self.env['hr.employee'].search([], order='id asc')
        leave_types = self.env['hr.leave.type'].search([], order='id asc')
        print(current_year, 'year')
        # Clear previous pivot report data
        self.env['leave.report.pivot'].search([]).unlink()

        # Get employee leave data for the current year
        emp_leave_data = leave_types.get_employees_days(employees.ids)

        for employee in employees:
            for leave_type_id in leave_types:
                # Check if there are leaves for the current year
                leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', employee.id),
                    ('holiday_status_id', '=', leave_type_id.id),
                    ('date_from', '>=', f'{current_year}-01-01'),
                    ('date_to', '<=', f'{current_year}-12-31'),
                ])

                if leaves:  # Only process if leaves exist for the current year
                    self.env['leave.report.pivot'].create({
                        'employee_id': employee.id,
                        'remaining_leaves': emp_leave_data[employee.id][leave_type_id.id]['virtual_remaining_leaves'],
                        'leave_type': leave_type_id.name,
                        'max_leaves': emp_leave_data[employee.id][leave_type_id.id]['max_leaves'],
                        'taken_leaves': emp_leave_data[employee.id][leave_type_id.id]['virtual_leaves_taken']
                    })
        # self.env['leave.report.pivot'].create({
        #     'employee_id': self.employee_id.id,
        #     'leave_type': self.leave_type.id
        # })

        return {'type': 'ir.actions.act_window',
                'res_model': 'leave.report.pivot',
                'view_mode': 'tree,pivot',
                'view_type': 'pivot',
                'res_id': self.id,
                'target': 'self'}

