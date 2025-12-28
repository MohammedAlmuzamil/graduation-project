from odoo import models,fields,api

from odoo.exceptions import UserError
from datetime import date
from odoo17.odoo.tools.populate import compute


class Order(models.Model):
    _name = 'order'
    _description = 'Order'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1,string="Number")
    name = fields.Integer(string = "Order ID", required = True, tracking = True)

    customer_id = fields.Many2one(
        'customer',
        string = "Customer Name",
        required = True,
        tracking = True
    )

    date_order = fields.Date(string = "Order Date", required = True, tracking = True, default = fields.Datetime.now())
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('sale', 'Sale'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], default='draft')


    line_ids = fields.One2many(
        'order.line',
        'order_id',
        string = "Order Lines"
    )

    total_quantity = fields.Float(
        compute="_compute_total",
        string="Total Quantity Kg",
        store=True
    )
    is_used_in_sale = fields.Boolean(string="Used In Sale", default=False)

    _sql_constraints = [
        ('unique_id', 'unique("order_id")', 'This Order ID Is Exist!')
    ]

    @api.constrains('name')
    def _check_order_id_validity(self):
        for rec in self:
            if not rec.name or rec.name <=0 :
                raise UserError("This Order ID Is Not Valid")




    @api.depends('line_ids.quantity')
    def _compute_total(self):
        for rec in self :
            rec.total_quantity = sum(line.quantity for line in rec.line_ids)


    @api.constrains('date_order')
    def _check_date_order_validity(self):
        for rec in self :
            if  rec.date_order > date.today():
                raise UserError("Sale Order Date  Cant Be In Future")


    def action_draft(self):
        for rec in self :
            rec.state = 'draft'

    def action_sent(self):
        for rec in self :
            rec.state = 'sent'

    def action_sale(self):
        for rec in self :
            rec.state = 'sale'

    def action_done(self):
        for rec in self :
            rec.state = 'done'

    def action_cancel(self):
        for rec in self :
            rec.state = 'cancel'





    @api.model
    def create(self, vals):
        res = super(Order, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('order_seq')
        return res


class OrderLine(models.Model):
    _name = 'order.line'
    _description = 'Order Line'


    order_id = fields.Many2one('order', ondelete='cascade')
    arabic_gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
        ('refined_gum', 'Residue Gum'),
    ], required=True, tracking=True, default='talha_gum', string="Arabic Gum Type")

    quantity = fields.Float(string="Quantity", required=True, tracking=True)

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self :
            if not rec.quantity or rec.quantity <= 0 :
                raise UserError(f"Quantity {rec.quantity} Must Be Greater Than Zero")