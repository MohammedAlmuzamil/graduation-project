from email.policy import default

from odoo import models,fields,api

from odoo.exceptions import UserError


class States(models.Model):
    _name = 'states'
    _description = 'States'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    state_id = fields.Integer(required=True,tracking=True,string="State ID")
    name = fields.Char(required=True, tracking=True, string="State Name")

    city_ids = fields.One2many(
        'cities',
        'state_id',
        string="Locality Name"
    )


    # غير في xml لانة غيرت العلاقه  -------------

    _sql_constraints = [
        ('unique_id', 'unique("state_id")', 'This State ID Is Exist!')
    ]




    @api.constrains('state_id')
    def _check_state_id_greater_than_zero(self):
        for rec in self :
            if not rec.state_id or rec.state_id <= 0 :
                raise UserError("Enter Valid Number For State ID")