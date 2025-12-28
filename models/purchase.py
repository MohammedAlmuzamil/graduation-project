from odoo import models,fields,api

from odoo.exceptions import UserError
from odoo17.odoo.tools.populate import compute
from datetime import date
import openai

class Purchase(models.Model):
    _name = 'purchase'
    _description = 'Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    ref = fields.Char(default='New', readonly=1,string="Number")
    active = fields.Boolean(default=True)
    name = fields.Integer(string="Purchase ID", required=True, tracking=True)

    total_price = fields.Float(
        string="Total Price",
        compute='_compute_total_price',
        store=True
    )

    purchase_date = fields.Date(string="Purchase Date", required=True, tracking=True, default=fields.Datetime.now())

    line_ids = fields.One2many('purchase.line', 'purchase_id', string="Purchase Lines")
    description = fields.Text(string="Note")
    commissioner_id = fields.Many2one(
        'commissioner',
        string="Commissioner",
        required=True
    )

    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse",
        required=True
    )

    order_id = fields.Many2one(
        'procure.order',
        string="Purchase Order ID",
        required=True,
        tracking=True,
        domain=[('state', '=', 'done'), ('is_used_in_purchase', '=', False)]
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('purchased', 'Purchased')
    ], string="Status", default='draft', tracking=True)

    is_transferred = fields.Boolean(string="Is Transferred", default=False)

    ai_analysis = fields.Text(string="AI Analysis (Arabic)", readonly=True)
    ai_analysis_visible = fields.Boolean(string="Show Analysis")


    _sql_constraints = [
        ('unique_purchase_id', 'unique(name)', 'This Purchase ID already exists!')
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
                analysis = f"العملية رقم {rec.name}: لا توجد بيانات للشراء.\n\n"
                all_analysis += analysis
                continue

            lines_summary = "\n".join([
                f"• {line.gum_type} - الكمية: {line.quantity}, السعر للوحدة: {line.unit_price}"
                for line in rec.line_ids
            ])

            prompt = (
                f"حلل بيانات عملية الشراء رقم {rec.name} وقدّم النتائج بالعربية "
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
            'name': 'Purchase AI Analysis',
            'res_model': 'purchase.analysis.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_analysis_text': all_analysis},
        }



    def purchase_xlsx_report(self):
        return {
            'type' : 'ir.actions.act_url',
            'url' : f'/purchase/excel/report/{self.env.context.get("active_ids")}',
            'target' : 'new'
        }

    @api.constrains('name')
    def _check_purchase_id_validity(self):
        for rec in self:
            if not rec.name or rec.name <= 0 :
                raise UserError("This Purchase ID Is Not Valid")


    @api.constrains('purchase_date')
    def _check_purchase_date_validity(self):
        for rec in self:
            if rec.purchase_date > date.today():
                raise UserError("Purchase Date Cant Be In Future")


    @api.onchange('order_id')
    def _onchange_order_id(self):
        if self.order_id:
            self.commissioner_id = self.order_id.commissioner_id.id
            self.line_ids = [(5, 0, 0)]
            lines = []
            for line in self.order_id.line_ids:
                lines.append((0, 0, {
                    'gum_type': line.arabic_gum_type,
                    'quantity': line.quantity,
                    'quality': line.quality,
                    'color': line.color,
                    'unit_price': line.unit_price,
                }))
            self.line_ids = lines


    @api.depends('line_ids.total_price')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = sum(line.total_price for line in rec.line_ids)



    @api.model
    def create(self, vals):
        res = super(Purchase, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('purchase_seq')
        return res

    def confirm_purchase(self):
        for purchase in self:
            if not purchase.commissioner_id:
                raise UserError("Commissioner must be set before confirming the purchase.")
            if not purchase.line_ids:
                raise UserError("No purchase lines found for this purchase.")

            last_record = self.env['arabic.gum.type'].search([], order="name desc", limit=1)
            next_name = int(last_record.name) + 1 if last_record else 1

            arabic_gum = self.env['arabic.gum.type'].create({
                'name': next_name,
            })

            if purchase.warehouse_id:
                arabic_gum.warehouse_ids = [(4, purchase.warehouse_id.id)]

            for line in purchase.line_ids:
                if not line.quantity:
                    raise UserError(f"Quantity cannot be empty for line: {line.gum_type}")

                purchase.state = 'purchased'
                self.env['arabic.gum.type.line'].create({
                    'arabic_gum_id': arabic_gum.id,
                    'arabic_gum_type': line.gum_type,
                    'quantity': line.quantity,
                    'color': line.color,
                    'quality': line.quality,
                })

                purchase.order_id.is_used_in_purchase = True








class PurchaseLine(models.Model):
    _name = 'purchase.line'
    _description = 'Purchase Line'

    purchase_id = fields.Many2one('purchase', string="Purchase Reference", required=True, ondelete='cascade')
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], string="Arabic Gum Type", required=True)

    color = fields.Selection([
        ('light_colored', 'Light Colored'),
        ('dark_colored', 'Dark Colored'),
    ], string="Color", required=True, default='light_colored')

    quality = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ], string="Quality", required=True, default='good')


    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", required=True)
    total_price = fields.Float(string="Total Price", compute='_compute_total_price', store=True)







    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.unit_price