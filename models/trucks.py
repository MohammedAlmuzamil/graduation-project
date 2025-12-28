from odoo import models,fields,api

from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class Trucks(models.Model):
    _name = 'trucks'
    _description = 'Trucks'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1,string="Number")
    name = fields.Integer( string="Truck ID", required=True , tracking=True)
    truck_type = fields.Selection([
        ('flatbed_truck','Flatbed Truck'),
        ('box_truck','Flatbed Box'),
        ('pickup_truck','Pickup Truck'),
        ('container_truck','Container Truck'),
    ],default='flatbed_truck',required=True , tracking=True)
    chassis_no = fields.Char(string="Chassis Number", required=True , tracking=True)
    license = fields.Char(string="License", required=True , tracking=True)
    max_weight = fields.Float(string="Max Weight KG", required=True , tracking=True)
    driver_id = fields.Many2one(
        'driver',
        string="Driver Name",
        required=True ,
        tracking=True
    )

    _sql_constraints = [
        ('unique_id', 'unique("truck_id")', 'This Truck ID Is Exist!')
    ]

    @api.constrains('truck_id')
    def _check_truck_id_greater_than_zero(self):
        for rec in self:
            if rec.truck_id <= 0:
                raise ValidationError('Please Add Valid Number of Truck ID')


    @api.model
    def create(self, vals):
        res = super(Trucks, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('trucks_seq')
        return res
