import re
from odoo import models,fields,api

from odoo17.odoo.exceptions import ValidationError


class Warehouseman(models.Model):
    _name = 'warehouseman'
    _description = 'Warehouseman'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=True)
    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse",
        tracking=True
    )
    employee_id = fields.Many2one(
        'employee',
        string="Employee Name",
        required=True,
        tracking=True
    )
    email = fields.Char(string="Email", tracking=True, default="example@email.com")
    address = fields.Text(string="Address", tracking=True)

    _sql_constraints = [
        ('unique_warehouse', 'unique(warehouse_id)', 'Each warehouse can have only one warehouseman!')
    ]

    @api.model
    def create(self, vals):
        res = super(Warehouseman, self).create(vals)

        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('warehouseman_seq')

        if res.warehouse_id:
            res.warehouse_id.warehouseman_id = res.id

        return res

    @api.constrains('email')
    def _check_email_validity(self):
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        for rec in self:
            if rec.email and not re.match(email_pattern, rec.email):
                raise ValidationError("Please enter a valid email address!")