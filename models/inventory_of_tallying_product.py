
from odoo import models,fields,api

from odoo17.odoo.exceptions import ValidationError, UserError
class InventoryOfTallyingProduct(models.Model):
    _name = 'inventory.of.tallying.product'
    _description = 'Inventory Of Tallying Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    product_id = fields.Char(string="Product ID", required=True, tracking=True)
    date = fields.Date(string="Date", required=True, tracking=True, default=fields.Datetime.now())
    description = fields.Text(string="Note", required=True, tracking=True)
    line_ids = fields.One2many(
        'inventory.of.tallying.product.line',
        'cleaning_id',
        string="Cleaning Details"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cleaned', 'Cleaned'),
    ], string="Status", default='draft', tracking=True)

    total_refined_text = fields.Char(compute="_compute_total_refined_text")

    @api.depends('line_ids.refined_quantity')
    def _compute_total_refined_text(self):
        for rec in self:
            total = sum(line.refined_quantity for line in rec.line_ids)
            rec.total_refined_text = total

    def action_load_all_gum_types(self):
        gum_types = self.env['arabic.gum.type'].search([('is_cleaned', '=', False)])
        if not gum_types:
            raise UserError("There is no record")

        lines = []
        for gum in gum_types:
            existing_line = self.line_ids.filtered(lambda l: l.gum_type_id == gum)
            if existing_line or gum.is_cleaned:
                continue

            lines.append((0, 0, {
                'gum_type_id': gum.id,
                'net_quantity': 0.0,
            }))

        if not lines:
            raise UserError("All gum types have already been cleaned or added.")

        self.write({'line_ids': lines})

    def action_clean_gums(self):
        if not self.line_ids:
            return {
                'warning': {
                    'title': "Warning",
                    'message': "No gum types to clean!",
                }
            }

        cleaned_lines = 0
        for line in self.line_ids:
            if line.net_quantity <= 0:
                continue
            if line.gum_type_id.is_cleaned:
                continue
            line.gum_type_id.write({'is_cleaned': True})
            cleaned_lines += 1

        if cleaned_lines == 0:
            return {
                'warning': {
                    'title': "Warning",
                    'message': "No new gum types were cleaned.",
                }
            }

        self.env['gum.stock'].recompute_stock()
        self.write({'state': 'cleaned'})
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Cleaning process completed successfully',
                'type': 'rainbow_man',
            }
        }


class InventoryOfTallyingProductLine(models.Model):
    _name = 'inventory.of.tallying.product.line'
    _description = 'Inventory Of Tallying Product Line'

    cleaning_id = fields.Many2one('inventory.of.tallying.product', string="Cleaning Reference", ondelete="cascade")
    gum_type_id = fields.Many2one('arabic.gum.type', string="Arabic Gum Type", required=True, ondelete='cascade')
    original_quantity = fields.Float(string="Original Quantity", related="gum_type_id.quantity", store=False, readonly=True)
    net_quantity = fields.Float(string="Quantity After Cleaning")
    refined_quantity = fields.Float(compute='_compute_refined_quantity', string="Refined Quantity")
    gum_type = fields.Selection(string="Gum Type", related="gum_type_id.arabic_gum_type", store=False, readonly=True)

    @api.depends('original_quantity', 'net_quantity')
    def _compute_refined_quantity(self):
        for rec in self:
            rec.refined_quantity = rec.original_quantity - rec.net_quantity

    @api.constrains('gum_type_id', 'cleaning_id')
    def _check_unique_gum_type_per_cleaning(self):
        for rec in self:
            if rec.cleaning_id and rec.gum_type_id:
                duplicates = rec.cleaning_id.line_ids.filtered(
                    lambda l: l.gum_type_id == rec.gum_type_id and l.id != rec.id)
                if duplicates:
                    raise ValidationError(
                        f"The gum type '{rec.gum_type_id.display_name}' is already added to this cleaning process."
                    )

    @api.model
    def create(self, vals):
        line = super().create(vals)
        self.env['gum.stock'].recompute_stock()
        return line

    def write(self, vals):
        res = super().write(vals)
        self.env['gum.stock'].recompute_stock()
        return res

#
# class InventoryOfTallyingProduct(models.Model):
#     _name = 'inventory.of.tallying.product'
#     _description = 'Inventory Of Tallying Product'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     active = fields.Boolean(default=True)
#
#     product_id = fields.Char(string = "Product ID", required = True, tracking = True)
#     # product_weight = fields.Float(string = "Product Weight KG", required = True, tracking = True)
#     # warehouse_id = fields.Many2one('warehouse',string = "Warehouse ID", required = True, tracking = True)
#     date = fields.Date(string = "Date", required = True, tracking = True,default=fields.Datetime.now())
#     # quantity_on_hand = fields.Float(string = "Quantity Available", required = True, tracking = True)
#     description = fields.Text(string = "Note", required = True, tracking = True)
#     line_ids = fields.One2many(
#         'inventory.of.tallying.product.line',
#         'cleaning_id',
#         string="Cleaning Details"
#     )
#
#     def action_load_all_gum_types(self):
#         gum_types = self.env['arabic.gum.type'].search([('is_cleaned', '=', False)])
#         if not gum_types:
#             raise UserError("There is no record")
#
#         lines = []
#         for gum in gum_types:
#             existing_line = self.line_ids.filtered(lambda l: l.gum_type_id == gum)
#             if existing_line or gum.is_cleaned:
#                 continue
#
#             lines.append((0, 0, {
#                 'gum_type_id': gum.id,
#                 'net_quantity': 0.0,
#             }))
#
#         if not lines:
#             raise UserError("All gum types have already been cleaned or added.")
#
#         self.write({'line_ids': lines})
#
#     total_refined_text = fields.Char(
#         compute="_compute_total_refined_text"
#     )
#
#     @api.depends('line_ids.refined_quantity')
#     def _compute_total_refined_text(self):
#         for rec in self:
#             total = sum(line.refined_quantity for line in rec.line_ids)
#             rec.total_refined_text =  total
#
#
#
# class InventoryOfTallyingProductLine(models.Model):
#     _name = 'inventory.of.tallying.product.line'
#     _description = 'Inventory Of Tallying Product Line'
#
#     cleaning_id = fields.Many2one('inventory.of.tallying.product', string="Cleaning Reference", ondelete="cascade")
#     gum_type_id = fields.Many2one('arabic.gum.type', string="Arabic Gum Type", required=True,ondelete='cascade')
#
#     original_quantity = fields.Float(string="Original Quantity", related="gum_type_id.quantity", store=False, readonly=True)
#     # raw_quantity = fields.Float(string="Raw Quantity Before Cleaning", required=True)
#     net_quantity = fields.Float(string="Quantity After Cleaning")
#     refined_quantity = fields.Float(compute='_compute_refined_quantity',string="Refined Quantity")
#     gum_type = fields.Selection(string="Gum Type", related="gum_type_id.arabic_gum_type", store=False, readonly=True)
#
#
#     @api.depends('original_quantity')
#     def _compute_refined_quantity(self):
#         for rec in self:
#             rec.refined_quantity = rec.original_quantity - rec.net_quantity
#
#     @api.constrains('gum_type_id', 'cleaning_id')
#     def _check_unique_gum_type_per_cleaning(self):
#         for rec in self:
#             if rec.cleaning_id and rec.gum_type_id:
#                 duplicates = rec.cleaning_id.line_ids.filtered(
#                     lambda l: l.gum_type_id == rec.gum_type_id and l.id != rec.id)
#                 if duplicates:
#                     raise ValidationError(
#                         f"The gum type '{rec.gum_type_id.display_name}' is already added to this cleaning process."
#                     )
#
#     @api.model
#     def create(self, vals):
#         gum_id = vals.get('gum_type_id')
#         if gum_id:
#             existing_line = self.env['inventory.of.tallying.product.line'].search([
#                 ('gum_type_id', '=', gum_id),
#                 ('net_quantity', '>', 0)
#             ], limit=1)
#             if existing_line:
#                 raise ValidationError("This gum type has already been cleaned. You cannot clean it again.")
#
#         line = super().create(vals)
#         self.env['gum.stock'].recompute_stock()
#         line.gum_type_id._compute_is_cleaned()
#         return line
#
#     def write(self, vals):
#         if 'net_quantity' in vals:
#             for rec in self:
#                 if rec.net_quantity > 0:
#                     raise ValidationError("This gum type has already been cleaned. You cannot modify it again.")
#         res = super().write(vals)
#         self.env['gum.stock'].recompute_stock()
#         for line in self:
#             line.gum_type_id._compute_is_cleaned()
#         return res
#
#
#
#     @api.model
#     def create(self, vals):
#         line = super().create(vals)
#         self.env['gum.stock'].recompute_stock()
#         return line
#
#     def write(self, vals):
#         res = super().write(vals)
#         self.env['gum.stock'].recompute_stock()
#         return res
#
#
