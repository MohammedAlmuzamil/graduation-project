from odoo import models,fields,api
import re

from odoo17.odoo.exceptions import ValidationError


class Driver(models.Model):
    _name = 'driver'
    _description = 'Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1,tracking=True, required=True)
    name = fields.Char(string="Driver Name", required=True,tracking=True)
    driver_id = fields.Integer(string="Driver ID", required=True,tracking=True)
    phone = fields.Char(default="+249", required=True,tracking=True)
    email = fields.Char(default="example@email.com", required=True,tracking=True)
    address = fields.Text(string="Address", required=True,tracking=True)

    _sql_constraints = [
        ('unique_id', 'unique("driver_id")', 'This ID Is Exist!')
    ]


    @api.model
    def default_get(self, fields_list):
        defaults = super(Driver, self).default_get(fields_list)
        last_record = self.search([], order='driver_id desc', limit=1)
        defaults['driver_id'] = (last_record.driver_id + 1) if last_record else 1
        return defaults

    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            if not vals['phone'].startswith('+249'):
                vals['phone'] = '+249' + vals['phone'].lstrip('0')

        if not vals.get('email'):
            vals['email'] = 'example@email.com'

        res = super(Driver, self).create(vals)

        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('driver_seq')

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