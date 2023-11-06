from odoo import models, fields, api


class EmployeePrivateNumber(models.Model):
    _inherit = 'hr.employee'

    private_number = fields.Char('Alternate Number')
    employee_id = fields.Char('Employee ID')


class HRLeavesActionCustomization(models.Model):
    _inherit = 'hr.leave'


