from odoo import models,fields,api

class Unit(models.Model):
    _name = 'unit'
    _description = 'Unit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    unit_name = fields.Selection([
        ('kilogram','Kilogram'),
        ('tonne','Tonne'),
    ],string="Unit Name", required=True,tracking=True)
    name = fields.Char(string="Unit ID", required=True,tracking=True)
    code = fields.Selection([
        ('kg','KG'),
        ('tn','TN'),
    ],default='kg',string="Gum Code", required=True,tracking=True,compute='_compute_code')

    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(Unit, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('unit_seq')
        return res

    @api.depends('unit_name')
    def _compute_code(self):
        for rec in self:
            if rec.unit_name == 'kilogram':
                rec.code = 'kg'
            else:
                rec.code ='tn'