import re
from odoo import models,fields,api

from odoo.exceptions import ValidationError


class Customer(models.Model):
    _name = 'customer'
    _description = 'Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1,string="Number")
    name = fields.Char(string="Customer Name", required=True)
    customer_id = fields.Integer(string="Customer ID", required=True)
    phone = fields.Char(string="Phone Number",tracking=True,default="+249")
    email = fields.Char(string="Email",tracking=True, default="example@gmail.com")
    address = fields.Text(string="Address",tracking=True)




    _sql_constraints = [
        ('unique_id', 'unique("customer_id")', 'This Customer ID Is Exist!')
    ]



    @api.model
    def default_get(self, fields_list):
        defaults = super(Customer, self).default_get(fields_list)
        last_record = self.search([], order='customer_id desc', limit=1)
        defaults['customer_id'] = (last_record.customer_id + 1) if last_record else 1
        return defaults




    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            if not vals['phone'].startswith('+249'):
                vals['phone'] = '+249' + vals['phone'].lstrip('0')

        if not vals.get('email'):
            vals['email'] = 'example@email.com'

        res = super(Customer, self).create(vals)

        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('customer_seq')

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
            if rec.phone:
                if not rec.phone.startswith('+249'):
                    raise ValidationError("Phone number must start with Sudan's code +249!")

                number_without_code = rec.phone[4:]
                if len(number_without_code) != 9 or not number_without_code.isdigit():
                    raise ValidationError("Phone number must contain exactly 9 digits after +249!")

    @api.constrains('customer_id')
    def _check_customer_id_validation(self):
        for rec in self :
            if not rec.customer_id or rec.customer_id <=0 :
                raise ValidationError("Customer ID Is Not Valid")