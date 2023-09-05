from odoo import models, fields


class RefusePublicHolidays(models.Model):
    _inherit = 'hr.leave'

    # def action_refuse_public_holiday(self):
    #     type_off = self.env['hr.leave'].search([])
    #     for i in type_off:
    #         if i.holiday_status_id.name == 'Public Holiday':
    #             if i.state == 'validate':
    #                 if i.holiday_type != 'company':
    #                     print(i.id, 'id')
    #                     i.action_refuse()
    #
    #                     print(i.holiday_status_id, 'holiday status')
    def action_refused_time_off(self):
        type_off = self.env['hr.leave'].search([])
        for i in type_off:
            if i.holiday_status_id.name == 'Public Holiday':
                if i.state == 'validate':
                    i.action_refuse()
