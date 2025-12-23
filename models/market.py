from odoo import models,fields,api

class Market(models.Model):
    _name = 'market'
    _description = 'Market'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    market_id = fields.Char(string="Market ID", required=True,tracking=True)
    name = fields.Char(string="Market Name", required=True,tracking=True)
    address_id = fields.Many2one('address',string="Market Address", required=True,tracking=True)

    _sql_constraints = [
        ('unique_id', 'unique("market_id")', 'This ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(Market, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('market_seq')
        return res