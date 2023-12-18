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
                              string='Branch')
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


class HRLeavesActionCustomization(models.Model):
    _inherit = 'hr.leave'
