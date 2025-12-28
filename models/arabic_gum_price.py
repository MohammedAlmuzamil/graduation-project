from odoo import models,fields,api
from odoo.exceptions import UserError

class ArabicGumPrice(models.Model):
    _name = 'arabic.gum.price'
    _description='Arabic Gum Price'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string="Arabic Gum ID",tracking=True,required=True)
    invoice_id = fields.Many2one('sale',string="Invoice ID",tracking=True,required=True)
    date = fields.Date(string="Price Date",tracking=True,required=True)
    units = fields.Many2one('unit',string="Unit ID",required=True,tracking=True)
    total_price = fields.Float(string="Total Amount",compute="_compute_total_price")
    line_ids = fields.One2many('arabic.gum.price.line','price_id')

    @api.depends('line_ids.subtotal')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = sum(line.subtotal for line in rec.line_ids)


class ArabicGumPriceLine(models.Model):
    _name = 'arabic.gum.price.line'
    _description='Arabic Gum Price'

    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
        ('refined_gum', 'Refined Gum')
    ], string="Gum Type", required=True)

    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", tracking=True)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)
    price_id = fields.Many2one('arabic.gum.price')


    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

