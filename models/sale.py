from odoo import models, fields, api

from odoo.exceptions import UserError
from datetime import date
import openai

class Sale(models.Model):
    _name = 'sale'
    _description = 'Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1, copy=False, string="Number")
    name = fields.Integer(string="Invoice Number", required=True, tracking=True)

    order_id = fields.Many2one(
        'order',
        string="Sale Order ID",
        required=True,
        tracking=True,
        domain=[('state', '=', 'done'), ('is_used_in_sale', '=', False)]
    )
    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse",
        required=True,
        tracking=True
    )
    employee_id = fields.Many2one(
        'employee',
        string="Employee",
        required=True,
        tracking=True
    )
    customer_id = fields.Many2one(
        'customer',
        string="Customer",
        required=True,
        tracking=True
    )
    sale_date = fields.Date(string="Sale Date", default=fields.Datetime.now, required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sold', 'Sold')
    ], string="Status", default='draft', tracking=True)

    line_ids = fields.One2many(
        'sale.line',
        'sale_id',
        string="Sale Lines"
    )
    amount_total = fields.Float(
        string="Total Price",
        compute="_compute_amount_total",
        store=True
    )

    check_returned = fields.Selection([
        ('pending', 'Pending'),
        ('returned', 'Returned')
    ], string="Is Returned", default='pending')

    ai_analysis = fields.Text(string="AI Analysis (Arabic)", readonly=True)
    ai_analysis_visible = fields.Boolean(string="Show Analysis", compute='_compute_ai_analysis_visible')



    _sql_constraints = [
        ('unique_invoice', 'unique(name)', 'This Invoice Number already exists!')
    ]

    def _text_to_html(self, text):
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

    def action_analyze_and_show(self):
        import openai
        openai.api_key = self.env['ir.config_parameter'].sudo().get_param('openai_api_key')

        all_analysis = ""

        for rec in self:
            if not rec.line_ids:
                analysis = f" {rec.name}: لا توجد بيانات بيع.\n\n"
                all_analysis += analysis
                continue

            lines_summary = "\n".join([
                f"• {line.gum_type} - الكمية: {line.quantity}, السعر للوحدة: {line.unit_price}"
                for line in rec.line_ids
            ])

            prompt = (
                f"حلل بيانات عمليات  البيع هذه {rec.name} وقدّم النتائج بالعربية "
                f"مع التوصيات وتقسيم الفقرات:\n{lines_summary}"
            )

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "أنت محلل بيانات ممتاز."},
                    {"role": "user", "content": prompt}
                ],
            )

            analysis = f"تحليل العملية {rec.name}:\n{response.choices[0].message.content}\n\n"
            all_analysis += analysis
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales AI Analysis',
            'res_model': 'sale.analysis.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_text': all_analysis},
        }



    def sales_xlsx_report(self):
        return {
            'type' : 'ir.actions.act_url',
            'url' : f'/sale/excel/report/{self.env.context.get("active_ids")}',
            'target' : 'new'
        }


    @api.constrains('name')
    def _check_sale_id_validity(self):
        for rec in self:
            if not rec.name or rec.name <= 0:
                raise UserError("This Invoice Number Is Not Valid")

    @api.constrains('sale_date')
    def _check_sale_date_validity(self):
        for rec in self:
            if rec.sale_date > date.today():
                raise UserError("Sale Date Cant Be In Future")

    @api.onchange('order_id')
    def _onchange_order_id(self):
        if self.order_id:
            self.line_ids = [(5, 0, 0)]
            lines = []
            for line in self.order_id.line_ids:
                lines.append((0, 0, {
                    'gum_type': line.arabic_gum_type,
                    'quantity': line.quantity,
                    'unit_price': 0.0,
                }))
            self.line_ids = lines

    def action_confirm_sale(self):
        for rec in self:
            if not self.line_ids:
                raise UserError("You Must Add At Least one Sale Line Before Confirming.")
            self._compute_amount_total()
            kg_unit = self.env['unit'].search([('code', '=', 'kg')], limit=1)
            price_rec = self.env['arabic.gum.price'].create({
                'name': rec.name,
                'invoice_id': rec.id,
                'date': fields.Date.today(),
                'units': kg_unit.id,
            })

            for line in rec.line_ids:
                self.env['arabic.gum.price.line'].create({
                    'gum_type': line.gum_type,
                    'quantity': line.quantity,
                    'unit_price': line.unit_price,
                    'price_id': price_rec.id,
                })
            rec.state = 'sold'
            self.message_post(body=f"Sale {self.ref} has been confirmed.")

            rec.order_id.is_used_in_sale = True
            return True

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(line.subtotal for line in rec.line_ids)

    def action_open_related_employee(self):
        action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.employee_action')
        view_id = self.env.ref('boraush_trading.employee_view_form').id
        action['res_id'] = self.employee_id.id
        action['views'] = [[view_id, 'form']]
        return action

    def action_open_related_customer(self):
        action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.customer_action')
        view_id = self.env.ref('boraush_trading.customer_view_form').id
        action['res_id'] = self.customer_id.id
        action['views'] = [[view_id, 'form']]
        return action

    def action_open_related_warehouse(self):
        action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.warehouse_action')
        view_id = self.env.ref('boraush_trading.warehouse_view_form').id
        action['res_id'] = self.warehouse_id.id
        action['views'] = [[view_id, 'form']]
        return action

    @api.model
    def create(self, vals):
        res = super(Sale, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('sale_seq')
        return res


class SaleLine(models.Model):
    _name = 'sale.line'
    _description = 'Sale Line'

    sale_id = fields.Many2one('sale', string="Sale Order", ondelete='cascade')
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
        ('refined_gum', 'Residue Gum')
    ], string="Gum Type", required=True)

    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", tracking=True)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleLine, self).create(vals_list)
        Stock = self.env['gum.stock'].sudo()
        stock = Stock.search([], limit=1)
        if not stock:
            raise UserError("No gum.stock record found. Please create a stock record first.")

        talha_delta = 0.0
        hashab_delta = 0.0
        olibanum_delta = 0.0
        refined_delta = 0.0

        for line in lines:
            qty = float(line.quantity or 0.0)
            if line.gum_type == 'talha_gum':
                talha_delta += qty
            elif line.gum_type == 'hashab_gum':
                hashab_delta += qty
            elif line.gum_type == 'olibanum_gum':
                olibanum_delta += qty
            elif line.gum_type == 'refined_gum':
                refined_delta += qty

        if (stock.talha_quantity or 0.0) < talha_delta:
            raise UserError("Not enough Talha Gum in stock!")
        if (stock.hashab_quantity or 0.0) < hashab_delta:
            raise UserError("Not enough Hashab Gum in stock!")
        if (stock.olibanum_quantity or 0.0) < olibanum_delta:
            raise UserError("Not enough Olibanum Gum in stock!")
        if (stock.refined_quantity or 0.0) < refined_delta:
            raise UserError("Not enough Refined Gum in stock!")
        new_vals = {
            'talha_quantity': (stock.talha_quantity or 0.0) - talha_delta,
            'hashab_quantity': (stock.hashab_quantity or 0.0) - hashab_delta,
            'olibanum_quantity': (stock.olibanum_quantity or 0.0) - olibanum_delta,
            'refined_quantity': (stock.refined_quantity or 0.0) - refined_delta,
        }
        stock.write(new_vals)

        return lines
