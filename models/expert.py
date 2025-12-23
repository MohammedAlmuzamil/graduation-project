from email.policy import default

from odoo import models,fields,api

class Expert(models.Model):
    _name = 'expert'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New',readonly=1)
    name = fields.Char(string="Expert Name" , required=True,tracking=True)
    expert_id = fields.Char(string="Expert ID", required=True,tracking=True)
    phone = fields.Char(string="Phone Number",tracking=True,default="+249")
    email = fields.Char(string="Email",tracking=True, default="example@email.com")
    address = fields.Text(string="Address",tracking=True)

    _sql_constraints = [
        ('unique_id', 'unique("expert_id")', 'This ID Is Exist!')
    ]


    @api.model
    def create(self,vals):
        res = super(Expert,self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('expert_seq')
        return res
