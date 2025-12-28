from email.policy import default

from odoo import models,fields,api
from odoo.exceptions import UserError

class Expert(models.Model):
    _name = 'expert'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New',readonly=1,string="Number")
    name = fields.Char(string="Expert Name" , required=True,tracking=True)

    expert_id = fields.Integer(string="Expert ID",required=True,tracking=True)

    phone = fields.Char(string="Phone Number",tracking=True,default="+249")
    email = fields.Char(string="Email",tracking=True, default="example@gmail.com")
    address = fields.Many2one(
        'address',
        string="Address",
        tracking=True
    )

    _sql_constraints = [
        ('unique_id', 'unique("expert_id")', 'This Expert ID Is Exist!')
    ]



    @api.model
    def create(self,vals):
        if not vals.get('expert_id'):
            vals['expert_id'] = self.env['ir.sequence'].next_by_code('expert_id')
        res = super(Expert,self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('expert_seq')
        return res


    @api.constrains('expert_id')
    def _check_expert_id_validation(self):
        for rec in self:
            if not rec.expert_id or rec.expert_id <=0:
                raise UserError("This Expert ID Is Not Valid")

    # @api.model
    # def create(self, vals):
    #     if not vals.get('expert_id'):
    #         vals['expert_id'] = self.env['ir.sequence'].next_by_code('expert_id')
    #     return super().create(vals)
