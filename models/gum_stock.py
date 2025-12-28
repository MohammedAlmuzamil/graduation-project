from odoo import models,fields,api

from odoo.exceptions import UserError


class GumStock(models.Model):
    _name = 'gum.stock'
    _description = 'Gum Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    talha_quantity = fields.Float(string="Talha On Hand Quantity",tracking=True)
    hashab_quantity = fields.Float(string="Hashab On Hand Quantity")
    olibanum_quantity = fields.Float(string="Olibanum On Hand Quantity")
    refined_quantity = fields.Float(string="Residue On Hand Quantity")

    update_date = fields.Date(string="Last Update On Stock")
    min_stock_level = fields.Float(string="Minimum Stock Level", tracking=True)
    max_stock_level = fields.Float(string="Maximum Stock Level", tracking=True)


    description = fields.Text(string="Note",tracking=True)

    total_quantity = fields.Float(
        string="Total On Hand Quantity",
        compute="_compute_total_quantity",
        store=True
    )


    @api.depends('talha_quantity', 'hashab_quantity', 'olibanum_quantity', 'refined_quantity')
    def _compute_total_quantity(self):
        for rec in self:
            rec.total_quantity = rec.talha_quantity + rec.hashab_quantity + rec.olibanum_quantity + rec.refined_quantity

    @api.constrains('talha_quantity', 'hashab_quantity', 'olibanum_quantity', 'refined_quantity')
    def _check_stock_levels(self):
        for rec in self:
            if rec.max_stock_level > 0:
                if rec.talha_quantity > rec.max_stock_level:
                    raise UserError(
                        f"Warning! Talha stock {rec.talha_quantity} exceeded the maximum level ({rec.max_stock_level}).")
                if rec.hashab_quantity > rec.max_stock_level:
                    raise UserError(
                        f"Warning! Hashab stock {rec.hashab_quantity} exceeded the maximum level ({rec.max_stock_level}).")
                if rec.olibanum_quantity > rec.max_stock_level:
                    raise UserError(
                        f"Warning! Olibanum stock {rec.olibanum_quantity} exceeded the maximum level ({rec.max_stock_level}).")
                if rec.refined_quantity > rec.max_stock_level:
                    raise UserError(
                        f"Warning! Refined stock {rec.refined_quantity} exceeded the maximum level ({rec.max_stock_level}).")

            if rec.min_stock_level > 0:
                if rec.talha_quantity < rec.min_stock_level:
                    raise UserError(
                        f"Warning! Talha stock ({rec.talha_quantity}) is below the minimum level ({rec.min_stock_level}).")
                if rec.hashab_quantity < rec.min_stock_level:
                    raise UserError(
                        f"Warning! Hashab stock ({rec.hashab_quantity}) is below the minimum level ({rec.min_stock_level}).")
                if rec.olibanum_quantity < rec.min_stock_level:
                    raise UserError(
                        f"Warning! Olibanum stock ({rec.olibanum_quantity}) is below the minimum level ({rec.min_stock_level}).")


    @api.model
    def recompute_stock(self):
        talha = 0.0
        hashab = 0.0
        olibanum = 0.0
        refined = 0.0
        lines = self.env['inventory.of.tallying.product.line'].search([])
        for line in lines:
            if not line.exists():
                continue
            gum_type = line.arabic_gum_type
            if gum_type == 'talha_gum':
                talha += float(line.net_quantity or 0.0)
            elif gum_type == 'hashab_gum':
                hashab += float(line.net_quantity or 0.0)
            elif gum_type == 'olibanum_gum':
                olibanum += float(line.net_quantity or 0.0)
            if hasattr(line, 'refined_quantity'):
                refined += float(line.refined_quantity or 0.0)

        stock = self.env['gum.stock'].search([], limit=1)
        if not stock:
            self.env['gum.stock'].create({
                'talha_quantity': talha,
                'hashab_quantity': hashab,
                'olibanum_quantity': olibanum,
                'refined_quantity': refined,
            })
        else:
            stock.write({
                'talha_quantity': talha,
                'hashab_quantity': hashab,
                'olibanum_quantity': olibanum,
                'refined_quantity': refined,
            })


