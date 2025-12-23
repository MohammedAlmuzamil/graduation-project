from email.policy import default

from odoo import models,fields,api

class Producer(models.Model):
    _name = 'producer'
    _description = 'Producer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    name = fields.Char(string="Producer Name", required=True,tracking=True)
    producer_id = fields.Char(string="Producer ID", required=True,tracking=True)
    phone = fields.Char(string="Phone", required=True,tracking=True)
    email = fields.Char(string="Email", required=True,tracking=True)
    address = fields.Text(string="Address", required=True,tracking=True)

    _sql_constraints = [
        ('unique_id', 'unique("producer_id")', 'This ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(Producer, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('producer_seq')
        return res
