from email.policy import default

from odoo import models,fields,api
from odoo.exceptions import UserError
class Localities(models.Model):
    _name = 'localities'
    _description = 'Localites'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    locality_id = fields.Integer(required=True,tracking=True,string="Locality ID")
    name = fields.Char(required=True,tracking=True,string="Locality Name")
    city_id = fields.Many2one('cities',required=True,tracking=True,string="City Name")


    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This Locality ID Is Exist!')
    ]

    @api.constrains('locality_id')
    def _check_locality_id_validation(self):
        for rec in self :
            if not rec.locality_id or rec.locality_id <= 0 :
                raise UserError("Enter Valid Number For Locality ID")

