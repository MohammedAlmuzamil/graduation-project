from email.policy import default

from odoo import models,fields,api
from odoo.exceptions import UserError

from odoo17.odoo.exceptions import UserError


class Cities(models.Model):
    _name = 'cities'
    _description = 'Cities'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    city_id = fields.Integer(required=True,tracking=True,string="City ID")
    name = fields.Char(required=True,tracking=True,string="City Name")

    state_id = fields.Many2one('states', required=True, tracking=True, string="State Name")


    localities_ids = fields.One2many(
        'localities',
        'city_id',
        string="Locality Name"
    )

    # just for pairing---------

    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This City ID Is Exist!')
    ]


    @api.constrains('city_id')
    def _check_city_id_validation(self):
        for rec in self :
            if not rec.city_id or rec.city_id <=0 :
                raise UserError("Enter Valid Number For City ID")
