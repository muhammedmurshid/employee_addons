from odoo import api, fields, models, _
import xlsxwriter
import base64
from datetime import datetime, date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('mobile_phone')
    def get_allocated_leaves(self):
        print('work')
        # Logic to fetch allocated leaves from the employee's record
        allocated_leaves = sum(self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.id),
            ('state', '=', 'validate'),
            # Add additional filters if needed
        ]).mapped('number_of_days'))
        # allocated_leaves = self.leave_allocation_field  # Replace with actual field name
        # print(allocated_leaves, 'allocated leaves')

        return allocated_leaves

    # @api.depends('mobile_phone')
    # def _taken_leaves(self):
    #     print(type(self.id), 'id')
    #     # Logic to calculate taken leaves from leave requests
    #     taken_leaves = self.env['hr.leave'].search([('employee_id', '=', 1),('state', '=', 'validate')])
    #     # raise UserError(self.name)
    #     print(taken_leaves, 'taken leaves')

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        for i in self:
            # print(type(vals['id']), 'id')
            # Logic to calculate taken leaves from leave requests
            # raise UserError(self.id)

            taken_leaves = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', i.id), ('state', '=', 'validate')])
            dicts = {}
            for rec in taken_leaves:
                # print(rec.number_of_days, 'number of days')
                ss = self.env['hr.leave.type'].search([('id', '=', rec.holiday_status_id.id)])
                if rec.holiday_status_id.name == ss.name:
                    # if dicts.get(rec.holiday_status_id.name):
                    try:
                        dicts[rec.holiday_status_id.name] += 1
                    except:
                        dicts[rec.holiday_status_id.name] = 1
                    # print(len(rec.holiday_status_id))
            # print(dicts, 'dicts')
            # print(ss.name, 'holiday type')

            # print(ss.name, 'name')
            # print(rec.holiday_status_id.name, 'taken leaves')

            allocated_leaves = sum(self.env['hr.leave.allocation'].search([
                ('employee_id', '=', i.id),
                ('state', '=', 'validate'),
                # Add additional filters if needed
            ]).mapped('number_of_days'))
            # allocated_leaves = self.leave_allocation_field  # Replace with actual field name
            # print(allocated_leaves, 'allocated leaves')

            leaves_taken = self.env['hr.leave.type'].search([
                ('name', '=', 'Public Holiday'),
                # Add additional filters if needed
            ])
            # print(leaves_taken.get_employees_days([1, 2]), 'leaves taken')

            # remaining_leaves = allocated_leaves - taken_leaves
            # print(remaining_leaves, 'remaining leaves')
            # return taken_leaves
            # raise UserError(taken_leaves)
            # return res

            # @api.onchange('mobile_phone')
            # def get_remaining_leaves(self):
            #     allocated_leaves = self.get_allocated_leaves()
            #     taken_leaves = self.get_taken_leaves()
            #
            #     remaining_leaves = allocated_leaves - taken_leaves
            #     print(remaining_leaves, 'remaining leaves')
            #     return remaining_leaves


class PrintLeavesReport(models.TransientModel):
    _name = 'print.leaves.report'
    _description = 'Print Leaves Report'

    excel_file = fields.Binary(string="Excel Report")
    filename = fields.Char(string="Filename")
    employee_id = fields.Many2one('hr.employee', string='Employee')

    def print_leaves_report(self):
        print('hello')
        employees = self.env['hr.employee'].search([], order='id asc')
        leave_types = self.env['hr.leave.type'].search([], order='id asc')
        workbook = xlsxwriter.Workbook('/tmp/hello.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
        money_format = workbook.add_format({'num_format': '$#,##0'})
        header_format = workbook.add_format()
        header_format.set_align('center')
        header_format.set_bold()
        worksheet.write(0, 0, 'Employee Name', bold)
        worksheet.set_column(0, 0, 20)

        row = 0
        col = 1
        for leave_type in leave_types:
            worksheet.merge_range(first_row=0, last_row=0, first_col=col, last_col=col + 2, data=leave_type.name,
                                  cell_format=header_format)
            worksheet.write(1, col, 'Remaining')
            worksheet.set_column(1, col, 13)

            worksheet.write(1, col + 1, 'Leave Taken')
            worksheet.set_column(1, col+1, 13)

            worksheet.write(1, col + 2, 'Leave Allotted')
            worksheet.set_column(1, col+2, 13)

            col += 3

        row = 2
        if self.employee_id:
            emp_ids = []
            emp_ids.append(self.employee_id.id)
            print(emp_ids, 'emp')
            # emp_ids.sort()
            emp_leave_data = leave_types.get_employees_days(emp_ids)
            print(emp_leave_data)
            for employee in employees:
                if employee.id == self.employee_id.id:
                    worksheet.write(row, 0, employee.name)
                    col = 1
                    for leave_type_id in emp_leave_data[employee.id].keys():
                        worksheet.write(row, col, emp_leave_data[employee.id][leave_type_id]['virtual_remaining_leaves'])
                        worksheet.set_column(row, col, 13)
                        worksheet.write(row, col + 1, emp_leave_data[employee.id][leave_type_id]['virtual_leaves_taken'])
                        worksheet.set_column(row, col + 1, 13)

                        worksheet.write(row, col + 2, emp_leave_data[employee.id][leave_type_id]['max_leaves'])
                        worksheet.set_column(row, col + 2, 13)

                        col += 3

                    row += 1

        else:
            emp_ids = employees.ids
            emp_ids.sort()
            emp_leave_data = leave_types.get_employees_days(emp_ids)
            print(emp_leave_data)
            for employee in employees:
                worksheet.write(row, 0, employee.name)
                col = 1
                for leave_type_id in emp_leave_data[employee.id].keys():
                    worksheet.write(row, col, emp_leave_data[employee.id][leave_type_id]['virtual_remaining_leaves'])
                    worksheet.set_column(row, col, 13)
                    worksheet.write(row, col+1, emp_leave_data[employee.id][leave_type_id]['virtual_leaves_taken'])
                    worksheet.set_column(row, col+1, 13)

                    worksheet.write(row, col+2, emp_leave_data[employee.id][leave_type_id]['max_leaves'])
                    worksheet.set_column(row, col+2, 13)

                    col+=3

                row += 1


        workbook.close()
        excel_file = base64.b64encode(open('/tmp/hello.xlsx', 'rb').read())
        self.excel_file = excel_file
        self.filename = 'Leaves Report'

        return {
            'name': 'Download Leaves Report',
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=print.leaves.report&id={}&field=excel_file&filename_field=filename&download=true'.format(
                self.id
            ),
            'target': 'self',
        }
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': '/invoicing/excel_report',
        #     'target': 'new',
        # }
        # print('hello')
        # leave = self.env['hr.leave'].search([])
        # return leave

    def view_of_report_pivot(self):
        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': 'Leaves Report',
            'view_mode': 'tree,pivot,form',
            'res_model': 'leave.report.pivot',
        }
