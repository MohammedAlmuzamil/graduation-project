from odoo import models,fields,api

class ArabicGum(models.Model):
    _name = 'arabic.gum'
    _description = 'Arabic Gum'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    arabic_gum_id = fields.Many2one('arabic.gum.type',string="Arabic Gum ID",required=True,tracking=True)
    warehouse_id = fields.One2many('warehouse','arabic_gum',string="Warehouse Name",required=True,tracking=True)
    quantity = fields.Integer(string="Quantity KG",required=True,tracking=True)
    date = fields.Date(string="Date",required=True,tracking=True,default=fields.Datetime.now())



    @api.model
    def create(self, vals):
        res = super(ArabicGum, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('arabic_gum_seq')
        return res
