from odoo import models,fields


class ArabicGumPrice(models.Model):
    _name = 'arabic.gum.price'
    _description='Arabic Gum Price'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    arabic_gum_id = fields.Many2one('arabic.gum.type',string="Arabic Gum ID",tracking=True)
    active = fields.Boolean(default=True)
    # gum_name = fields.Selection([
    #     ('talha_gum','Talha Gum'),
    #     ('hashab_gum','Hashab Gum'),
    #     ('olibanum_gum','Olibanum Gum'),
    # ],required=True,tracking=True,related='arabic_gum_id.arabic_gum_type')

    # gum_name = fields.Char(string="Gum Name", related='arabic_gum_id.arabic_gum_type',readonly=True,tracking=True)
    gum_name = fields.Integer(related='arabic_gum_id.name',readonly=0,  string="Gum Name", tracking=True)
    units = fields.Many2one('unit',string="Unit ID",required=True,tracking=True)
    unit_price = fields.Float(string="Unit Price",required=True,tracking=True)
    price_date = fields.Date(string="Price Date",required=True,tracking=True,default=fields.Datetime.now())
