from email.policy import default

from odoo import models,fields,api
from odoo.exceptions import UserError
class Address(models.Model):
    _name = 'address'
    _description = 'Address'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref = fields.Char(default='New', readonly=1,string="Number")
    active = fields.Boolean(default=True)
    
    # the above field we are using it for adding archiving feature to my record just adding it in tree form view


    # -------------------------------------
    # state_id = fields.Integer(required=True,tracking=True,string="State ID")
    # state_name = fields.Selection([
    #     ('khartoum', 'Khartoum'),
    #     ('north_kordofan', 'North Kordofan'),
    #     ('south_kordofan', 'South Kordofan'),
    #     ('west_kordofan', 'West Kordofan'),
    #     ('north_darfur', 'North Darfur'),
    #     ('south_darfur', 'South Darfur'),
    #     ('east_darfur', 'East Darfur'),
    #     ('west_darfur', 'West Darfur'),
    #     ('central_darfur', 'Central Darfur'),
    #     ('river_nile', 'River Nile'),
    #     ('northern', 'Northern'),
    #     ('red_sea', 'Red Sea'),
    #     ('kassala', 'Kassala'),
    #     ('gedaref', 'Gedaref'),
    #     ('sennar', 'Sennar'),
    #     ('blue_nile', 'Blue Nile'),
    #     ('white_nile', 'White Nile'),
    #     ('gezira', 'Gezira'),
    # ])
    # locality_id = fields.Integer(required=True,tracking=True,string="Locality ID")
    # locality_name = fields.Char(required=True,tracking=True,string="Locality Name")
    # ------------------------------------------ old address class before formatting


    address_id = fields.Integer(string="Address ID",required=True, tracking=True)



    name = fields.Many2one('localities',string="Address")
    postcode = fields.Char(required=True,tracking=True,string="Postcode")
    street_no = fields.Char(required=True,tracking=True,string="Street Number")
    building_no = fields.Char(required=True,tracking=True,string="Building Number")


    _sql_constraints = [
        ('unique_id', 'unique("address_id")', 'This Address ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(Address, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('address_seq')
        return res

    @api.constrains('address_id')
    def _check_address_id_validation(self):
        for rec in self :
            if not rec.address_id or rec.address_id <=0 :
                raise UserError("Enter Valid Number For Address ID")


