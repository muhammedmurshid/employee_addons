from odoo import models, fields, api
from odoo.http import request
from odoo import http


class InvoiceExcelReportController(http.Controller):
    @http.route(['/invoicing/excel_report'], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, report_id=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Invoice_report' + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # get data for the report.
        report_lines = report_id.get_report_lines()
        # prepare excel sheet styles and formats
        sheet = workbook.add_worksheet("invoices")
        sheet.write(1, 0, 'No.', header_style)
        sheet.write(1, 1, 'Invoice Reference', header_style)
        sheet.write(1, 2, 'Customer', header_style)

        row = 2
        number = 1
        # write the report lines to the excel document
        for line in report_lines:
            sheet.set_row(row, 20)
            sheet.write(row, 0, number, text_style)
            sheet.write(row, 1, line['move_id'], text_style)
            sheet.write(row, 2, line['partner_id'], text_style)
            row += 1
            number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
