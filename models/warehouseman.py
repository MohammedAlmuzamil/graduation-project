import re
from odoo import models,fields,api

from odoo.exceptions import ValidationError
from datetime import date

class Warehouseman(models.Model):
    _name = 'warehouseman'
    _description = 'Warehouseman'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=True,string="Number")
    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse",
        tracking=True
    )
    name = fields.Many2one(
        'employee',
        string="Employee Name",
        required=True,
        tracking=True
    )
    employee_id = fields.Integer(
        related="name.employee_number",
        store=False,
        readonly=True
    )
    email = fields.Char(string="Email", tracking=True, default="example@gmail.com")
    address = fields.Many2one(
        'address',
        string="Address",
        tracking=True
    )
    hire_date = fields.Date(string="Hire Date", default=fields.Datetime.now, required=True, tracking=True)

    _sql_constraints = [
        ('unique_warehouse', 'unique(warehouse_id)', 'Each warehouse can have only one warehouseman!')
    ]


    @api.constrains('hire_date')
    def _check_hire_date_validity(self):
        for rec in self:
            if rec.hire_date > date.today():
                raise ValidationError("Hire Date Cant Be In Future")


    @api.model
    def create(self, vals):
        res = super(Warehouseman, self).create(vals)

        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('warehouseman_seq')

        if res.warehouse_id:
            res.warehouse_id.warehouseman_id = res.id

        return res

    def write(self, vals):
        res = super(Warehouseman, self).write(vals)
        for rec in self:
            if rec.warehouse_id:
                rec.warehouse_id.warehouseman_id = rec.id
        return res



    @api.constrains('email')
    def _check_email_validity(self):
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        for rec in self:
            if rec.email and not re.match(email_pattern, rec.email):
                raise ValidationError("Please enter a valid email address!")