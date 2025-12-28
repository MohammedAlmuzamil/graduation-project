import re
from datetime import date

from odoo import models,fields,api

from odoo.exceptions import ValidationError

from datetime import date


class Employee(models.Model):
    _name = 'employee'
    _description = 'Employee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string="Employee Name",tracking=True)
    employee_number = fields.Integer(string="Employee ID", required=True,tracking=True)
    phone = fields.Char(string="Phone Number",tracking=True,default="+249")
    email = fields.Char(string="Email",tracking=True, default="example@gmail.com")

    job_id = fields.Many2one(
        'job',
        string="Job",
        required=True,
        tracking=True
    )

    hire_data = fields.Date(string="Hire Date",tracking=True,default=fields.Datetime.now())
    address = fields.Many2one(
        'address',
        string="Address",
        tracking=True
    )

    _sql_constraints = [
        ('unique_id', 'unique("employee_number")', 'This Employee ID Is Exist!')
    ]



    @api.model
    def default_get(self, fields_list):
        defaults = super(Employee, self).default_get(fields_list)
        last_record = self.search([], order='employee_number desc', limit=1)
        defaults['employee_number'] = (last_record.employee_number + 1) if last_record else 1
        return defaults

    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            if not vals['phone'].startswith('+249'):
                vals['phone'] = '+249' + vals['phone'].lstrip('0')

        if not vals.get('email'):
            vals['email'] = 'example@email.com'

        res = super(Employee, self).create(vals)
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


    @api.constrains('employee_number')
    def _check_employee_number_validation(self):
        for rec in self :
            if not rec.employee_number or rec.employee_number <=0 :
                raise ValidationError("Employee ID Is Not Valid")


    @api.constrains('hire_data')
    def _check_hire_data_validation(self):
        for rec in self :
            if rec.hire_data > date.today():
                raise ValidationError("Hire Date Cant Be In Future")