from email.policy import default

from odoo import models,fields,api

class Address(models.Model):
    _name = 'address'
    _description = 'Address'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref = fields.Char(default='New', readonly=1)
    active = fields.Boolean(default=True)
    name = fields.Integer(string="Address ID",required=True,tracking=True)
    continent = fields.Selection([
        ('africa','Africa'),
        ('asia','Asia'),
        ('europe','Europe'),
        ('north_america','North America'),
        ('south_america','South America'),
        ('australia','Australia'),
    ],required=True,tracking=True,string="Continent Name",default='africa')
    country_id = fields.Integer(required=True,tracking=True,string="Country ID")
    country_name = fields.Char(required=True,tracking=True,string="Country Name")
    state_id = fields.Integer(required=True,tracking=True,string="State ID")
    state_name = fields.Char(required=True,tracking=True,string="State Name")
    locality_id = fields.Integer(required=True,tracking=True,string="Locality ID")
    locality_name = fields.Char(required=True,tracking=True,string="Locality Name")
    city_id = fields.Integer(required=True,tracking=True,string="City ID")
    city_name = fields.Char(required=True,tracking=True,string="City Name")

    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(Address, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('address_seq')
        return res

