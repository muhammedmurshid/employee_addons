from odoo import models, fields, api, _
from datetime import datetime, date


class EmployeePrivateNumber(models.Model):
    _inherit = 'hr.employee'

    private_number = fields.Char('Alternate Number')
    employee_id = fields.Char('Employee ID')
    branch = fields.Selection([('corporate_office', 'Corporate Office'), ('cochin_campus', 'Cochin Campus'),
                               ('kottayam_campus', 'Kottayam Campus'), ('calicut_campus', 'Calicut Campus'),
                               ('malappuram_campus', 'Malappuram Campus'), ('trivandrum_campus', 'Trivandrum Campus'),
                               ('palakkad_campus', 'Palakkad Campus'), ('dubai_campus', 'Dubai Campus'),
                               ('jk_shah_classes', 'JK Shah Classes')],
                              string='Testing Branch')
    branch_id = fields.Many2one('logic.base.branches', string='Branch')
    age = fields.Integer(string='Age', readonly=True, compute="_compute_calculate_age", store=True)

    def calculate_employee_age(self):
        today = date.today()
        rec = self.env['hr.employee'].sudo().search([])
        for i in rec:
            if i.birthday:
                a = today.year - i.birthday.year - ((today.month, today.day) < (i.birthday.month, i.birthday.day))
                i.age = a
            else:
                i.age = 0

    @api.depends('birthday')
    def _compute_calculate_age(self):
        for i in self:
            today = date.today()
            if i.birthday:
                age = today.year - i.birthday.year - ((today.month, today.day) < (i.birthday.month, i.birthday.day))
                i.age = age

    # def old_branch_to_new_branch_employee(self):
    #     rec = self.env['hr.employee'].sudo().search([])
    #     print('working')
    #     for record in rec:
    #         if record.branch:
    #
    #             if record.branch == 'corporate_office':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 1})
    #             if record.branch == 'cochin_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 2})
    #             if record.branch == 'malappuram_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 9})
    #             if record.branch == 'kottayam_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 3})
    #             if record.branch == 'calicut_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 4})
    #             if record.branch == 'trivandrum_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 6})
    #             if record.branch == 'palakkad_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 7})
    #             if record.branch == 'dubai_campus':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 8})
    #             if record.branch == 'jk_shah_classes':
    #                 print(record.name, record.branch)
    #                 record.update({'branch_id': 13})


class MonthOfBirthAddServerAction(models.Model):
    _inherit = 'hr.employee'

    def action_add_month_of_birth(self):
        employees = self.env['hr.employee'].sudo().search([('birthday', '!=', False)])
        for employee in employees:
            print(employee.name, 'name')
            if employee.birthday:
                if employee.birthday.month == 1:
                    print("hii")
                    employee.birth_month = 'january'
                elif employee.birthday.month == 2:
                    employee.birth_month = 'february'
                elif employee.birthday.month == 3:
                    employee.birth_month = 'march'
                elif employee.birthday.month == 4:
                    print(employee.birthday.month)
                    employee.birth_month = 'april'
                elif employee.birthday.month == 5:
                    print(employee.birthday.month)
                    employee.birth_month = 'may'
                elif employee.birthday.month == 6:
                    print(employee.birthday.month)
                    employee.birth_month = 'june'
                elif employee.birthday.month == 7:
                    print(employee.birthday.month)
                    employee.birth_month = 'july'
                elif employee.birthday.month == 8:
                    print(employee.birthday.month)
                    employee.birth_month = 'august'
                elif employee.birthday.month == 9:
                    print(employee.birthday.month)
                    employee.birth_month = 'september'
                elif employee.birthday.month == 10:
                    print(employee.birthday.month)
                    employee.birth_month = 'october'
                elif employee.birthday.month == 11:
                    print(employee.birthday.month)
                    employee.birth_month = 'november'
                elif employee.birthday.month == 12:
                    print(employee.birthday.month)
                    employee.birth_month = 'december'
                else:
                    print("incorrect month")

    def send_birthday_reminder(self):
        # Get today's date
        today = datetime.today()
        print(today.month, today.day, 'today')

        # Find employees whose date of birth is today
        employees_with_birthday = self.search([
            ('birthday', '!=', False),  # Ensure birthday is set
            ('active', '=', True)  # Only active employees
        ])

        # Collect employees whose birthday is today
        birthday_employees = self.env['hr.employee']  # Initialize an empty recordset

        for employee in employees_with_birthday:
            print(employee.birthday.day, employee.birthday.month, 'pp')
            if employee.birthday.month == today.month and employee.birthday.day == today.day:
                print(employee.name, 'emp')
                birthday_employees |= employee  # Add employee to the recordset

        print(birthday_employees, 'employees')

        if birthday_employees:
            # Get the HR manager (assuming there is one HR manager user)
            hr_manager = self.env['hr.department'].search([('name', '=', 'HR')], limit=1).manager_id
            if hr_manager:
                # Prepare the email content with employee names
                employee_names = ', '.join(birthday_employees.mapped('name'))

                # Prepare mail values
                mail_values = {
                    'subject': 'Employee Birthday Reminder',
                    'body_html': f'''
                        <p>Dear {hr_manager.name},</p>
                        <p>The following employees have birthdays today:</p>
                        <ul>{"".join([f"<li>{employee.name}</li>" for employee in birthday_employees])}</ul>
                        <p>Best regards,<br/>Your HR System</p>
                    ''',
                    'email_to': hr_manager.work_email,
                }

                print(hr_manager.work_email, 'mail')

                # Create and send the email
                self.env['mail.mail'].create(mail_values).send()
            else:
                print("No HR manager found.")
        else:
            print("No employees with birthdays today.")
