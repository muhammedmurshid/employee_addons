import io
import xlsxwriter
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.http import request
from odoo import http
from pytz import timezone


class AttendanceExcelReportController(http.Controller):
    @http.route([
        '/attendance/excel_report/<model("attendance.report.employees.wizard"):report_id>',
    ], type='http', auth="user", csrf=False)
    def get_attendance_excel_report(self, report_id=None, from_date=None, company_id=None, to_date=None, **args):
        # Convert dates from string to datetime
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        company_id = report_id.company_id.id
        print(company_id, 'kom')
        # Prepare the response to download the file
        if report_id.report_type == 'attendance':
            # Prepare the response to download the file if the report type is 'attendance'
            response = request.make_response(
                None,
                headers=[
                    ('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename="Attendance_report.xlsx"')
                ]
            )

            # Create an in-memory output stream
            output = io.BytesIO()
            self.generate_attendance_report(output, from_date, to_date, company_id)

            output.seek(0)
            response.stream.write(output.read())
            output.close()
            return response

        else:
            # If the report type is not 'attendance', return a different response or no file
            return request.render('some_template',
                                  {'message': 'No attendance report to generate for this report type.'})

        # Create an in-memory output stream
        # output = io.BytesIO()
        # self.generate_attendance_report(output, from_date, to_date, company_id)
        #
        # output.seek(0)
        # response.stream.write(output.read())
        # output.close()
        # return response

    def generate_attendance_report(self, output, from_date, to_date, company_id):
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Attendance Report")

        # Define some formats similar to the uploaded file's format
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9EAD3', 'border': 1})
        text_format = workbook.add_format({'align': 'center', 'border': 1})
        wf_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#5ef27a', 'font_color': 'black'})
        sw_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#f29a63', 'font_color': 'black'})

        # Define formats for attendance status
        absent_format = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': 'red', 'font_color': 'white'})
        half_day_format = workbook.add_format(
            {'align': 'center', 'border': 1, 'bg_color': '#00BFFF', 'font_color': 'white'})  # Primary blue
        public_holiday_format = workbook.add_format(
            {'align': 'center', 'border': 1, 'bg_color': 'yellow', 'font_color': 'black'})  # Yellow for public holidays

        # Generate dynamic date range
        date_range = [(from_date + timedelta(days=i)) for i in range((to_date - from_date).days + 1)]

        # Write headers (Date and Day)
        headers = ['DATE', 'DAY'] + [str(date.day) for date in date_range] + ['PRESENT (P)', 'HALF DAY (HD)',
                                                                              'ABSENT (A)', 'SUNDAY WORKING (SW)', 'WORK FROM HOME (WF)']
        subheaders = ['SL NO.', 'NAME'] + [date.strftime('%a').upper() for date in date_range] + ['P', 'HD', 'A', 'SW', 'WF']

        for col_num, col_data in enumerate(headers):
            sheet.write(0, col_num, col_data, header_format)

        for col_num, col_data in enumerate(subheaders):
            sheet.write(1, col_num, col_data, header_format)

        # Fetch employee data
        employees = request.env['hr.employee'].search([('active', '=', True),('user_id.faculty_check', '=', False), ('department_id.name', '!=', 'DIRECTORS')])  # Fetch all employees

        # Fetch leave data for all employees within the date range
        leaves = request.env['hr.leave'].search([
            ('date_from', '<=', to_date),
            ('date_to', '>=', from_date),
            ('state', 'in', ['validate','head_approve']),
        ])
        sunday_working = []
        leave_allocations = request.env['hr.leave.allocation'].search([('date_allocation', '<=', to_date), ('date_allocation', '>=', from_date),('state', 'in', ['validate','head_approve']), ('holiday_status_id.name', '=', 'Sunday Working')])
        for i in leave_allocations:
            sunday_working.append(i.date_allocation)
            print(i.date_allocation, 'allo')
        print(sunday_working, 'sunday')
        work_from_home = []
        leave_allocations_work = request.env['hr.leave.allocation'].search(
            [('date_allocation', '<=', to_date), ('date_allocation', '>=', from_date),
             ('state', 'in', ['validate','head_approve']), ('holiday_status_id.name', '=', 'Work from Home')])
        for j in leave_allocations_work:
            work_from_home.append(j.date_allocation)

        print(work_from_home, 'wf')
        public_holidays = []

        # Fetch public holiday data from the calendar
        holiday_calendar = request.env['resource.calendar'].search(
            [('company_id', '=', company_id), ('global_leave_ids', '!=', False)], limit=1)

        # Get the user's timezone
        user_tz = request.env.user.tz or 'UTC'  # Fallback to UTC if no timezone is set
        user_tz_obj = timezone(user_tz)

        for leave in holiday_calendar.global_leave_ids:
            leave_in_user_tz = leave.date_from.astimezone(user_tz_obj)
            leave_from_date = leave_in_user_tz.date()

            if from_date <= leave_from_date <= to_date:
                public_holidays.append(leave_from_date)

        # Write employee data
        row = 2
        for index, employee in enumerate(employees, start=1):
            sheet.write(row, 0, index, text_format)
            sheet.write(row, 1, employee.name, text_format)

            # Initialize counters for each status
            present_count = 0
            half_day_count = 0
            absent_count = 0
            sunday_working_count = 0
            work_from_home_count = 0

            # Filter Sunday working allocations for this employee
            employee_sunday_work_allocations = leave_allocations.filtered(
                lambda a: a.employee_id == employee and a.holiday_status_id.name == 'Sunday Working'
            )

            # Filter Work From Home allocations for this employee
            employee_work_from_home_allocations = leave_allocations_work.filtered(
                lambda a: a.employee_id == employee and a.holiday_status_id.name == 'Work from Home'
            )

            for col_num, date in enumerate(date_range, start=2):
                # Default to 'P' for present
                status = 'P'
                status_format = text_format  # Default format

                if date in public_holidays:
                    status = 'PH'  # Public Holiday
                    status_format = public_holiday_format

                elif date.weekday() == 6:  # Sunday
                    # Check if the employee has a valid Sunday Working allocation for this Sunday
                    if employee_sunday_work_allocations.filtered(lambda a: a.date_allocation == date):
                        status = 'SW'  # Mark as Sunday Working
                        status_format = sw_format
                    else:
                        status = 'A'  # Absent if there's no Sunday Working allocation
                        status_format = absent_format

                elif date in work_from_home:
                    # Check if the employee has a Work From Home allocation for the current date
                    if employee_work_from_home_allocations.filtered(lambda a: a.date_allocation == date):
                        status = 'WF'  # Work from Home
                        status_format = wf_format

                # Check if the employee has any leave for the current date
                employee_leaves = leaves.filtered(
                    lambda l: l.employee_id == employee and l.date_from.date() <= date <= l.date_to.date()
                )
                if employee_leaves:
                    leave = employee_leaves[0]  # Get the first leave for simplicity
                    leave_type = leave.holiday_status_id.name  # Get the leave type name

                    if leave.request_unit_half:
                        status = 'HD'  # Half-day leave
                        status_format = half_day_format  # Use half-day format
                    else:
                        status = leave_type  # Use the leave type name instead of "A"
                        status_format = absent_format  # Use absent format

                # Increment the appropriate counter based on the status
                if status == 'P':
                    present_count += 1
                elif status == 'HD':
                    half_day_count += 1
                elif status != 'P' and status != 'HD':  # Check for leave type (absent with leave type name)
                    absent_count += 1

                # Write status to the Excel file with the corresponding format
                sheet.write(row, col_num, status, status_format)

            # Write the totals for the employee at the end of the row
            sheet.write(row, col_num + 1, present_count, text_format)
            sheet.write(row, col_num + 2, half_day_count, text_format)
            sheet.write(row, col_num + 3, absent_count, text_format)
            sheet.write(row, col_num + 4, sunday_working_count, text_format)
            sheet.write(row, col_num + 5, work_from_home_count, text_format)

            row += 1
        workbook.close()
