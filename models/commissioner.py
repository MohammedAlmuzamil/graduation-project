import re

from odoo import models,fields,api

from odoo.exceptions import ValidationError


class Commissioner(models.Model):
    _name = 'commissioner'
    _description = 'Commissioner'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New' , readonly=1,string="Number")
    name = fields.Char(string="Commissioner Name" , required=True,tracking=True)
    comm_id = fields.Integer(string="Commissioner ID" , required=True,tracking=True)
    phone = fields.Char(string="Phone Number",tracking=True,default="+249")
    email = fields.Char(string="Email",tracking=True, default="example@gmail.com")
    address = fields.Many2one(
        'address',
        string="Address",
        tracking=True
    )


    _sql_constraints = [
        ('unique_id', 'unique("comm_id")', 'This Commissioner ID Is Exist!')
    ]



    @api.model
    def default_get(self, fields_list):
        defaults = super(Commissioner, self).default_get(fields_list)
        last_record = self.search([], order='comm_id desc', limit=1)
        defaults['comm_id'] = (last_record.comm_id + 1) if last_record else 1
        return defaults

    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            if not vals['phone'].startswith('+249'):
                vals['phone'] = '+249' + vals['phone'].lstrip('0')

        if not vals.get('email'):
            vals['email'] = 'example@email.com'

        res = super(Commissioner, self).create(vals)

        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('commissioner_seq')

        return res

    @api.constrains('email')
    def _check_email_validity(self):
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        for rec in self:
            if rec.email and not re.match(email_pattern, rec.email):
                raise ValidationError("Please enter a valid email address!")


    @api.constrains('phone')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone and not rec.phone.startswith('+249'):
                raise ValidationError("Phone number must start with Sudan's code +249!")


    @api.constrains('comm_id')
    def _check_comm_id(self):
        for rec in self:
            if not rec.comm_id or rec.comm_id <=0 :
                raise ValidationError("Commissioner ID Is Not Valid")

