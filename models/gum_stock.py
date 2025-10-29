from odoo import models,fields,api

class GumStock(models.Model):
    _name = 'gum.stock'
    _description = 'Gum Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    talha_quantity = fields.Float(string="Talha On Hand Quantity", readonly=True,tracking=True)
    hashab_quantity = fields.Float(string="Hashab On Hand Quantity", readonly=True)
    olibanum_quantity = fields.Float(string="Olibanum On Hand Quantity", readonly=True)

    talha_price = fields.Float(string="Talha Gum Price")
    hashab_price = fields.Float(string="Hashab Gum Price")
    olibanum_price = fields.Float(string="Olibanum Gum Price")

    description = fields.Text(string="Note",tracking=True)

    @api.model
    def recompute_stock(self):
        talha = 0.0
        hashab = 0.0
        olibanum = 0.0

        lines = self.env['inventory.of.tallying.product.line'].search([])
        for line in lines:
            if not line.exists():
                continue
            gum_type = line.gum_type_id.arabic_gum_type
            if gum_type == 'talha_gum':
                talha += line.net_quantity
            elif gum_type == 'hashab_gum':
                hashab += line.net_quantity
            elif gum_type == 'olibanum_gum':
                olibanum += line.net_quantity

        stock = self.env['gum.stock'].search([], limit=1)
        if not stock:
            stock = self.env['gum.stock'].create({
                'talha_quantity': talha,
                'hashab_quantity': hashab,
                'olibanum_quantity': olibanum,
                'unit_price': 0.0
            })
        else:
            stock.write({
                'talha_quantity': talha,
                'hashab_quantity': hashab,
                'olibanum_quantity': olibanum,
            })