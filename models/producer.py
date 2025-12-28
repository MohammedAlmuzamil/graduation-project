from email.policy import default
import re

from odoo import models,fields,api
from odoo.exceptions import UserError,ValidationError
from datetime import date



class Producer(models.Model):
    _name = 'producer'
    _description = 'Producer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    name = fields.Char(string="Producer Name", required=True,tracking=True)
    producer_id = fields.Integer(string="Producer ID", required=True,tracking=True)
    phone = fields.Char(string="Phone", required=True,tracking=True,default="+249")
    email = fields.Char(string="Email", required=True,tracking=True, default="example@gmail.com")
    address = fields.Many2one('address', string="Address", tracking=True)
    hire_data = fields.Date(string="Hire Date", tracking=True, default=fields.Datetime.now())
    _sql_constraints = [
        ('unique_id', 'unique("producer_id")', 'This Producer ID Is Exist!')
    ]


    @api.constrains('producer_id')
    def _check_producer_id_validity(self):
        for rec in self:
            if not rec.producer_id or rec.producer_id <=0 :
                raise UserError("This Producer ID Is Not Valid")



    @api.constrains('hire_data')
    def _check_hire_data_validity(self):
        for rec in self:
            if rec.hire_data > date.today():
                raise ValidationError("Hire Date Cant Be In Future")



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



    @api.model
    def create(self, vals):
        res = super(Producer, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('producer_seq')
        return res
