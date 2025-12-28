import re
from odoo import models,fields,api

from odoo.exceptions import ValidationError


class Supervisor(models.Model):
    _name = 'supervisor'
    _description = 'Supervisor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New' , readonly=1,string="Number")
    name = fields.Char(string="Supervisor Name",tracking=True,required=True)
    supervisor_id = fields.Integer(string="Supervisor ID",tracking=True,required=True)
    phone = fields.Char(string="Phone Number",tracking=True,required=True,default="+249")
    email = fields.Char(string="Email",tracking=True,required=True, default="example@gmail.com")
    address = fields.Many2one(
        'address',
        string="Address",
        tracking=True
    )
    hire_date = fields.Date(string="Hire Date",tracking=True,required=True,default=fields.Datetime.now())

    _sql_constraints = [
        ('unique_id', 'unique("supervisor_id")', 'This Supervisor ID Is Exist!')
    ]

    @api.constrains('supervisor_id')
    def _check_supervisor_id_validity(self):
        for rec in self:
            if not rec.supervisor_id or rec.supervisor_id <=0 :
                raise ValidationError("This Supervisor ID Is Not Valid")



    @api.model
    def default_get(self, fields_list):
        defaults = super(Supervisor, self).default_get(fields_list)
        last_record = self.search([], order='supervisor_id desc', limit=1)
        defaults['supervisor_id'] = (last_record.supervisor_id + 1) if last_record else 1
        return defaults

    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            if not vals['phone'].startswith('+249'):
                vals['phone'] = '+249' + vals['phone'].lstrip('0')

        if not vals.get('email'):
            vals['email'] = 'example@email.com'

        res = super(Supervisor, self).create(vals)

        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('supervisor_seq')

        return res

    @api.constrains('email')
    def _check_email_validity(self):
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        for rec in self:
            if rec.email and not re.match(email_pattern, rec.email):
                raise ValidationError("Please Enter A Valid Email Address!")



    @api.constrains('phone')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone and not rec.phone.startswith('+249'):
                raise ValidationError("Phone Number Must Start With Sudan's Code +249!")
