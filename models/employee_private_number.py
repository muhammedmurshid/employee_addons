from odoo import models, fields, api


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

    def get_old_branch_to_new_branch(self):
        rec = self.env['hr.employee'].sudo().search([])
        for record in rec:
            if record.branch:
                if record.branch == 'Kottayam Campus':
                    record.branch = 3
                if record.branch == 'Corporate Office':
                    record.branch = 1
                if record.branch == 'Cochin Campus':
                    record.branch = 1
                if record.branch == 'Trivandrum Campus':
                    record.branch = 6
                if record.branch == 'Calicut Campus':
                    record.branch = 4
                if record.branch == 'Malappuram Campus':
                    record.branch = 9
                if record.branch == 'Palakkad Campus':
                    record.branch = 7

                if record.branch == 'Online Campus':
                    record.branch = 10
                if record.branch == 'Dubai Campus':
                    record.branch = 8
                if record.branch == 'JK Shah Classes':
                    record.branch = 13


class HRLeavesActionCustomization(models.Model):
    _inherit = 'hr.leave'
