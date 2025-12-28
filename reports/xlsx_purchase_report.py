from ast import literal_eval
from docutils.utils.smartquotes import options
from odoo import http
from odoo.http import request
import io
import xlsxwriter



class XlsxPurchaseReport(http.Controller):


    @http.route('/purchase/excel/report/<string:purchase_ids>' , type='http' , auth='user')
    def download_purchase_excel_report(self,purchase_ids):
        purchase_ids = request.env['purchase'].browse(literal_eval(purchase_ids))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output ,{'in_memory' : True})
        worksheet = workbook.add_worksheet('Purchases')

        header_format = workbook.add_format({
            'bold' : True ,
            'bg_color' : '#eb861e',
            'border' : 3 ,
            'align' : 'center',
            'font_color': 'white'
        })

        string_format = workbook.add_format({
            'border' : 2 ,
            'align' : 'center'
        })

        price_format = workbook.add_format({
            'border' : 2 ,
            'align' : 'center',
            'num_format' : '$##,##00.00'
        })

        number_format = workbook.add_format({
            'border' : 2 ,
            'align' : 'center'
        })

        date_format = workbook.add_format({
            'border': 2,
            'align': 'center',
            'num_format': 'dd-mm-yyyy'
        })


        headers = [
            'Purchase ID' ,
            'Precure Order' ,
            'Purchase Date' ,
            'Commissioner Name',
            'Warehouse Name',
            'Gum Type' ,
            'Color' ,
            'Quality' ,
            'Quantity' ,
            'Unit Price' ,
            'Total Price'
        ]
        for col_num , header in enumerate(headers):
            worksheet.write(0 , col_num , header , header_format)

        row_num = 1

        for purchase in purchase_ids:
            for line in purchase.line_ids:
                gum_type = dict(line._fields['gum_type'].selection).get(line.gum_type, '')
                color = dict(line._fields['color'].selection).get(line.color, '')
                quality = dict(line._fields['quality'].selection).get(line.quality, '')

                worksheet.write(row_num, 0, purchase.name, number_format)
                worksheet.write(row_num, 1, purchase.order_id.name if purchase.order_id else '', number_format)
                worksheet.write(row_num, 2, purchase.purchase_date, date_format)
                worksheet.write(row_num, 3, purchase.commissioner_id.name if purchase.commissioner_id else '',string_format)
                worksheet.write(row_num, 4, purchase.warehouse_id.name if purchase.warehouse_id else '', string_format)

                worksheet.write(row_num, 5, gum_type or '', string_format)
                worksheet.write(row_num, 6, color or '', string_format)
                worksheet.write(row_num, 7, quality or '', string_format)
                worksheet.write(row_num, 8, line.quantity or 0, number_format)
                worksheet.write(row_num, 9, line.unit_price or 0.0, price_format)
                worksheet.write(row_num, 10, line.total_price or 0.0, price_format)

                row_num += 1


        workbook.close()
        output.seek(0)
        file_name = 'Purchase Report.xlsx'
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type','application/vnd.openxmlformats-officedocuments.spreadsheetml.sheet'),
                ('Content-disposition' , f'attachment; filename={file_name}')
            ]
        )