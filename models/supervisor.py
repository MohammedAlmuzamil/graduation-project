import re
from odoo import models,fields,api

from odoo17.odoo.exceptions import ValidationError


class Supervisor(models.Model):
    _name = 'supervisor'
    _description = 'Supervisor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New' , readonly=1)
    name = fields.Char(string="Supervisor Name",tracking=True,required=True)
    supervisor_id = fields.Integer(string="Supervisor ID",tracking=True,required=True)
    phone = fields.Char(string="Phone Number",tracking=True,required=True,default="+249")
    email = fields.Char(string="Email",tracking=True,required=True, default="example@email.com")
    address = fields.Text(string="Address",tracking=True,required=True)
    hire_date = fields.Date(string="Hire Date",tracking=True,required=True,default=fields.Datetime.now())

    _sql_constraints = [
        ('unique_id', 'unique("supervisor_id")', 'This ID Is Exist!')
    ]


    # @api.model
    # def create(self,vals):
    #     res = super(Supervisor,self).create(vals)
    #     if res.ref == 'New':
    #         res.ref = self.env['ir.sequence'].next_by_code('supervisor_seq')
    #     return res

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
                raise ValidationError("Please enter a valid email address!")

    @api.constrains('phone')
    def _check_phone_number(self):
        for rec in self:
            if rec.phone and not rec.phone.startswith('+249'):
                raise ValidationError("Phone number must start with Sudan's code +249!")
