from odoo import models,fields,api

class Order(models.Model):
    _name = 'order'
    _description = 'Order'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    order_id = fields.Char(string = "Order ID", required = True, tracking = True)
    gum_id = fields.Many2one('arabic.gum.type',string="Gum Type")
    gum_type = fields.Selection(related='gum_id.arabic_gum_type')
    quantity = fields.Float(string = "Quantity", required = True, tracking = True)
    customer_id = fields.Many2one('customer',string = "Customer Name", required = True, tracking = True)
    date_order = fields.Date(string = "Order Date", required = True, tracking = True, default = fields.Datetime.now())

    _sql_constraints = [
        ('unique_id', 'unique("order_id")', 'This ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(Order, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('order_seq')
        return res