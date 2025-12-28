from odoo import models,fields,api

from odoo.api import depends
from odoo.exceptions import UserError,ValidationError
from datetime import date

class ProcureOrder(models.Model):
    _name = 'procure.order'
    _description='Procure Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    name = fields.Integer(string="Procure Order ID",tracking=True,required=True)
    commissioner_id = fields.Many2one(
        'commissioner',
        string="Commissioner Name"
    )

    date = fields.Date(string = "Procure Order Date", required = True, tracking = True, default = fields.Datetime.now())

    line_ids = fields.One2many(
        'procure.order.line',
        'procure_id',
        string = "Procure Lines"
    )

    total_amount = fields.Float(
        string="Subtotal $ "
        , compute="_compute_total",
        store=True
    )
    total_amount_quantity = fields.Float(
        string="Total Quantity Kg",
        compute="_compute_total_quantity",
        store=True
    )

    state = fields.Selection([
        ('draft','Draft'),
        ('sent','Sent'),
        ('to_approve','To Approve'),
        ('purchase','Purchase'),
        ('done','Done'),
        ('cancel','Cancel'),
    ],default='draft')

    is_used_in_purchase = fields.Boolean(string="Used In Purchase", default=False)

    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This Procure Order ID Is Exist!')
    ]

    @api.constrains('name')
    def _check_procure_order_validity(self):
        for rec in self :
            if not rec.name or rec.name <=0 :
                raise UserError("This Procure Order ID Is Not Valid")


    @api.constrains('date')
    def _check_procure_order_date_validity(self):
        for rec in self:
            if rec.date < date.today():
                raise UserError("Procure Order Date  Cant Be In Future")



    @api.depends('line_ids.quantity','line_ids.unit_price')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(line.quantity * line.unit_price for line in rec.line_ids)



    @api.depends('line_ids.quantity')
    def _compute_total_quantity(self):
        for rec in self:
            rec.total_amount_quantity = sum(line.quantity for line in rec.line_ids)



    def action_draft(self):
        for rec in self :
            rec.state = 'draft'

    def action_sent(self):
        for rec in self :
            rec.state = 'sent'

    def action_to_approve(self):
        for rec in self :
            rec.state = 'to_approve'

    def action_purchase(self):
        for rec in self :
            rec.state = 'purchase'

    def action_done(self):
        for rec in self :
            rec.state = 'done'

    def action_cancel(self):
        for rec in self :
            rec.state = 'cancel'





    @api.model
    def create(self, vals):
        res = super(ProcureOrder, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('procure_order_seq')
        return res


class ProcureOrderLine(models.Model):
    _name = 'procure.order.line'
    _description = 'Procure Order Line'


    procure_id = fields.Many2one('procure.order', ondelete='cascade')
    quality = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ], required=True, tracking=True, default='good', string="Quality")
    arabic_gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required=True, tracking=True, default='talha_gum', string="Arabic Gum Type")
    color = fields.Selection([
        ('light_colored', 'Light Colored'),
        ('dark_colored', 'Dark Colored'),
    ], required=True, tracking=True, string="Color", default='light_colored')
    quantity = fields.Float(string="Quantity", required=True, tracking=True)
    unit_price = fields.Float(string="Unit Price", required=True, tracking=True)


    @api.constrains('quantity')
    def _check_quantity_validity(self):
        for rec in self:
            if not rec.quantity or rec.quantity <=0.0 :
                raise ValidationError("Quantity Cant Be Zero Or Less")




    @api.constrains('unit_price')
    def _check_unit_price_validity(self):
        for rec in self:
            if not rec.unit_price or rec.unit_price <=0 :
                raise ValidationError("Unit Price Cant Be Zero Or Less")