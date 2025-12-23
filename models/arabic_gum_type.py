from odoo import models,fields,api

from odoo17.odoo.exceptions import ValidationError


class ArabicGumType(models.Model):
    _name = 'arabic.gum.type'
    _description = 'Arabic Gum Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    name = fields.Integer(required=True,tracking=True,string="Arabic Gum ID")
    arabic_gum_type = fields.Selection([
        ('talha_gum','Talha Gum'),
        ('hashab_gum','Hashab Gum'),
        ('olibanum_gum','Olibanum Gum'),
    ],required=True,tracking=True,default='talha_gum',string="Arabic Gum Type")
    color = fields.Selection([
        ('light_colored','Light Colored'),
        ('dark_colored','Dark Colored'),
    ],required=True,tracking=True,string="Color",default='light_colored')
    quality = fields.Selection([
        ('excellent','Excellent'),
        ('very_good','Very Good'),
        ('good','Good'),
        ('average','Average'),
        ('poor','Poor'),
    ],required=True,tracking=True,default='good',string="Quality")

    quantity = fields.Float(required=True,tracking=True,string="Quantity")
    date = fields.Date(string="Date",required=True,tracking=True,default=fields.Datetime.now())
    warehouse_ids = fields.Many2many(
        'warehouse',
        string="Warehouses"
    )

    line_ids = fields.One2many(
        'inventory.of.tallying.product.line',
        'gum_type_id',
        string="Cleaning Lines"
    )


    is_cleaned = fields.Boolean(
        string="Cleaned",
        compute="_compute_is_cleaned",
        store=True
    )

    @api.depends('line_ids.net_quantity')
    def _compute_is_cleaned(self):
        for rec in self:
            rec.is_cleaned = any(line.net_quantity > 0 for line in rec.line_ids)

    @api.constrains('name')
    def _check_name_positive(self):
        for rec in self:
            if rec.name <= 0:
                raise ValidationError("Inter Valid Number For Gum ID")


    @api.model
    def create(self, vals):
        res = super(ArabicGumType, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('arabic_gum_type_seq')
        return res