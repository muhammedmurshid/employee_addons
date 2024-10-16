from odoo import fields,models,api,_

class AttendanceReport(models.Model):
    _name = 'attendance.report.employees.wizard'

    from_date = fields.Date(string='From Date', required=1)
    to_date = fields.Date(string='To Date', required=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=1)
    report_type = fields.Selection([('attendance', 'Attendance'), ('leaves','Leaves')], string='Report Type')

    def generate_attendance_report(self):
        # Redirect to the route that generates the Excel report
        if self.report_type == 'attendance':
            # Redirect to the route that generates the Attendance Excel report
            return {
                'type': 'ir.actions.act_url',
                'url': '/attendance/excel_report/%s?from_date=%s&to_date=%s' % (
                    self.id, self.from_date, self.to_date),
                'target': 'self',
            }
        elif self.report_type == 'leaves':
            # Redirect to the route that generates the Leave Excel report (you would create this route similarly)
            return {
                'type': 'ir.actions.act_url',
                'url': '/leave/excel_report/%s?from_date=%s&to_date=%s' % (
                    self.id, self.from_date, self.to_date),
                'target': 'self',
            }

    def get_report_lines(self):
        invoice_list = []
        for move in self.env['hr.employee'].search([('active', '=', True)]):

            if move:
                line = {'employee': move.name,
                        # 'partner_id': move.partner_id.name,
                        }
                invoice_list.append(line)

        return invoice_list

    def get_employee_public_holidays(self):
        # Fetch all active employees


        # Dictionary to store public holidays for each employee
        employee_holidays = {}
        holiday = self.env['resource.calendar'].search([('company_id.id', '=', self.company_id.id), ('global_leave_ids', '!=', False)], limit=1)
            # Fetch public holidays associated with the calendar

        for i in holiday.global_leave_ids:
            print(i.name, 'hh')

                # Store the holidays in a list
