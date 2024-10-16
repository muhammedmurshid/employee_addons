import io
import xlsxwriter
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.http import request
from odoo import http
from pytz import timezone

class LeavesExcelReport(http.Controller):
    @http.route([
        '/leave/excel_report/<model("attendance.report.employees.wizard"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_leave_excel_report(self, report_id=None, from_date=None, to_date=None, **args):
        # Similar to the attendance report, you'll convert dates, prepare response, and generate the Excel
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename="Leave_report.xlsx"')
            ]
        )

        output = io.BytesIO()
        self.generate_leave_report(output, from_date, to_date)
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response

    def generate_leave_report(self, output, from_date, to_date):
        # Create an Excel workbook and add a worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Leave Report")

        # Define formats for headers, sub-headers, and text
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9EAD3', 'border': 1})
        subheader_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#F4CCCC', 'border': 1})
        text_format = workbook.add_format({'align': 'center', 'border': 1})
        total_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#FFEB9C', 'border': 1})

        # Main headers: SL NO., EMPLOYEE
        main_headers = ['SL NO.', 'EMPLOYEE']

        # Sub headers for Time Off and Allocation under each leave type
        leave_types = request.env['hr.leave.type'].search([])
        sub_headers = []

        for leave_type in leave_types:
            main_headers.append(leave_type.name)  # Leave type as the main header
            sub_headers.append('Time Off')
            sub_headers.append('Allocation')

        main_headers.append('TOTAL')  # Add TOTAL column

        # Write main headers to the first row
        sheet.write(0, 0, 'SL NO.', header_format)
        sheet.write(0, 1, 'EMPLOYEE', header_format)

        # Write leave types as headers and merge columns for each leave type
        col_num = 2  # Start after SL NO. and EMPLOYEE
        for leave_type in leave_types:
            sheet.merge_range(0, col_num, 0, col_num + 1, leave_type.name, header_format)  # Merge leave type columns
            col_num += 2

        sheet.write(0, col_num, 'TOTAL', header_format)  # Write TOTAL header

        # Write subheaders (Time Off and Allocation) in the second row
        col_num = 2  # Start after SL NO. and EMPLOYEE
        for _ in leave_types:
            sheet.write(1, col_num, 'Time Off', subheader_format)
            sheet.write(1, col_num + 1, 'Allocation', subheader_format)
            col_num += 2

        sheet.write(1, col_num, 'TOTAL', subheader_format)  # Write TOTAL subheader

        row = 2  # Data rows start from row 2
        # Dictionary to store total days for each leave type across all employees
        leave_totals = {leave_type.id: {'time_off': 0, 'allocation': 0} for leave_type in leave_types}

        # Fetch all active employees
        employees = request.env['hr.employee'].search([('active', '=', True)])

        # Loop through employees and fill in the report
        for index, employee in enumerate(employees, start=1):
            sheet.write(row, 0, index, text_format)  # SL NO.
            sheet.write(row, 1, employee.name, text_format)  # EMPLOYEE

            total_days = 0  # To calculate the total leave days for this employee
            col_num = 2  # Start column after SL NO. and EMPLOYEE

            for leave_type in leave_types:
                # Fetch time off for the employee and this leave type
                time_off_leaves = request.env['hr.leave'].search([
                    ('employee_id', '=', employee.id),
                    ('holiday_status_id', '=', leave_type.id),
                    ('date_from', '>=', from_date),
                    ('date_to', '<=', to_date),
                    ('state', 'in', ['validate', 'head_approve']),
                ])

                time_off_days = sum(leave.number_of_days for leave in time_off_leaves)
                leave_totals[leave_type.id]['time_off'] += time_off_days  # Add to global total for this leave type

                # Fetch leave allocations for this employee and leave type
                leave_allocations = request.env['hr.leave.allocation'].search([
                    ('employee_id', '=', employee.id),
                    ('holiday_status_id', '=', leave_type.id),
                    ('state', 'in', ['validate', 'head_approve']),
                ])

                allocation_days = sum(allocation.number_of_days for allocation in leave_allocations)
                leave_totals[leave_type.id]['allocation'] += allocation_days  # Add to allocation total

                total_days += time_off_days  # Add time off days to employee's total

                # Write time off and allocation data for this leave type
                sheet.write(row, col_num, time_off_days, text_format)
                sheet.write(row, col_num + 1, allocation_days, text_format)
                col_num += 2

            # Write the total leave days for this employee at the end of the row
            sheet.write(row, col_num, total_days, text_format)
            row += 1

        # Write totals for each leave type at the bottom
        col_num = 2  # Start after SL NO. and EMPLOYEE
        sheet.write(row, 1, 'TOTAL', total_format)

        for leave_type in leave_types:
            sheet.write(row, col_num, leave_totals[leave_type.id]['time_off'],
                        total_format)  # Total time off for leave type
            sheet.write(row, col_num + 1, leave_totals[leave_type.id]['allocation'], total_format)  # Total allocation
            col_num += 2

        # Write the grand total of all leave types in the final column
        sheet.write(row, col_num, sum([leave_totals[lt]['time_off'] for lt in leave_totals]), total_format)

        workbook.close()



