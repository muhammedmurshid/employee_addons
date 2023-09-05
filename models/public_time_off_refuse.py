from odoo import api, fields, models, _


class PublicTimeOffRefuse(models.Model):
    _inherit = 'hr.leave'

    def refuse_public_holiday(self):
        type_off = self.env['hr.leave'].search([])
        for i in type_off:
            if i.holiday_status_id.name == 'Public Holiday':
                if i.state == 'validate':
                    i.action_refuse()
