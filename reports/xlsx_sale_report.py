from ast import literal_eval
from docutils.utils.smartquotes import options
from odoo import http
from odoo.http import request
import io
import xlsxwriter


class XlsxSaleReport(http.Controller):

    @http.route('/sale/excel/report/<string:sale_ids>' , type='http' , auth='user')
    def download_sale_excel_report(self , sale_ids):
        sale_ids = request.env['sale'].browse(literal_eval(sale_ids))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output , {'in_memory' : True})
        worksheet = workbook.add_worksheet('Sales')
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#eb861e',
            'border': 3,
            'align': 'center',
            'font_color': 'white'
        })

        string_format = workbook.add_format({
            'border': 2,
            'align': 'center'
        })

        price_format = workbook.add_format({
            'border': 2,
            'align': 'center',
            'num_format': '$##,##00.00'
        })

        number_format = workbook.add_format({
            'border': 2,
            'align': 'center'
        })

        date_format = workbook.add_format({
            'border': 2,
            'align': 'center',
            'num_format': 'dd-mm-yyyy'
        })

        headers = [
            'Invoice Number',
            'Sale Order ID',
            'Sale Date',
            'Warehouse Name',
            'Employee Name',
            'Customer Name',
            'Gum Type',
            'Quantity',
            'Unit Price',
            'Total Price'
        ]


        for col_num , header in enumerate(headers):
            worksheet.write(0 , col_num , header , header_format)


        row_num = 1
        for sale in sale_ids:
            for line in sale.line_ids:
                gum_type = dict(line._fields['gum_type'].selection).get(line.gum_type , '')

                worksheet.write(row_num , 0 , sale.name , number_format)
                worksheet.write(row_num , 1 , sale.order_id.name if sale.order_id else '' , number_format)
                worksheet.write(row_num , 2 , sale.sale_date , date_format)
                worksheet.write(row_num , 3 , sale.warehouse_id.name if sale.warehouse_id else '' , string_format)
                worksheet.write(row_num , 4 , sale.employee_id.name if sale.employee_id else '' , string_format)
                worksheet.write(row_num , 5 , sale.customer_id.name if sale.customer_id else '' , string_format)
                worksheet.write(row_num , 6 , gum_type or '' , string_format)
                worksheet.write(row_num , 7 , line.quantity or 0 , number_format)
                worksheet.write(row_num , 8 , line.unit_price or 00.00 , price_format)
                worksheet.write(row_num , 9 , line.subtotal or 00.00 , price_format)
                row_num += 1


        workbook.close()
        output.seek(0)
        file_name = 'Sale Report.xlsx'
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocuments.spreadsheetml.sheet'),
                ('Content-disposition', f'attachment; filename={file_name}')
            ]
        )