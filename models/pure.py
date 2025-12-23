from odoo import models,fields,api
from odoo.exceptions import UserError
from odoo17.odoo.exceptions import ValidationError, UserError


class Pure(models.Model):
    _name = 'pure'
    _description = 'Pure'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    name = fields.Char(string="Pure ID",required=True,tracking=True)
    pure_type = fields.Selection([
        ('raw','Raw'),
        ('bark','Bark'),
    ],default='raw',string="Pure Type",required=True,tracking=True)
    quantity = fields.Float(string="Quantity kg",required=True,tracking=True)
    warehouse_id = fields.Many2one('warehouse',string="Warehouse",required=True,tracking=True)
    date = fields.Date(string="Date", required=True, tracking=True, default=fields.Datetime.now())


    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This ID Is Exist!')
    ]


    @api.constrains('quantity')
    def _check_quantity_greater_than_zero(self):
        for rec in self:
            if not rec.quantity or rec.quantity <= 0:
                raise UserError('Please Enter A Valid Quantity Greater Than Zero.')

    @api.model
    def create(self, vals):
        res = super(Pure, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('pure_seq')
        return res