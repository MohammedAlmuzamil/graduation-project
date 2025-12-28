from odoo import models,fields,api

from odoo.exceptions import ValidationError,UserError


class ArabicGumType(models.Model):
    _name = 'arabic.gum.type'
    _description = 'Arabic Gum Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=True, string="Number")
    name = fields.Integer(required=True, tracking=True, string="Arabic Gum ID")
    date = fields.Date(string="Date", required=True, tracking=True, default=fields.Datetime.now())

    warehouse_ids = fields.Many2many('warehouse', string="Warehouses")

    line_gum_ids = fields.One2many(
        'arabic.gum.type.line',
        'arabic_gum_id',
        string="Arabic Gum Types Lines"
    )

    total_quantity = fields.Float(compute="_compute_total", string="Total Quantity Kg", store=True)

    @api.depends('line_gum_ids.quantity')
    def _compute_total(self):
        for rec in self:
            rec.total_quantity = sum(line.quantity for line in rec.line_gum_ids)

    @api.constrains('name')
    def _check_name_positive(self):
        for rec in self:
            if rec.name <= 0:
                raise ValidationError("Enter a valid Number for Gum ID")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('arabic_gum_type_seq')
        return res


class ArabicGumTypeLine(models.Model):
    _name = 'arabic.gum.type.line'
    _description = 'Arabic Gum Type Line'

    arabic_gum_id = fields.Many2one('arabic.gum.type', string="Arabic Gum")

    arabic_gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required=True, tracking=True, default='talha_gum', string="Arabic Gum Type")

    color = fields.Selection([
        ('light_colored', 'Light Colored'),
        ('dark_colored', 'Dark Colored'),
    ], required=True, tracking=True, default='light_colored', string="Color")

    quality = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ], required=True, tracking=True, default='good', string="Quality")

    quantity = fields.Float(required=True, tracking=True, string="Quantity")

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self :
            if rec.quantity <= 0 :
                raise UserError(f" Quantity Cant be Negative NO")