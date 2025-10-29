from odoo import models, fields, api
from odoo17.odoo.exceptions import UserError

class Returns(models.Model):
    _name = 'returns'
    _description = 'Returns'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=True)
    return_id = fields.Char(string="Return ID", required=True, tracking=True)
    return_date = fields.Date(string="Return Date", default=fields.Datetime.now, required=True, tracking=True)
    sale_id = fields.Many2one('sale', string="Sale Reference", required=True, tracking=True)
    customer_id = fields.Many2one('customer', string="Customer Name", readonly=True)
    line_ids = fields.One2many('returns.line', 'return_id', string="Return Lines")
    return_reason_id = fields.Text(string="Return Reason", required=True, tracking=True)

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        if self.sale_id:
            self.customer_id = self.sale_id.customer_id.id
            self.line_ids = [(0, 0, {
                'sale_line_id': line.id,
                'gum_type': line.gum_type,
                'quantity': line.quantity,
                'unit_price': line.unit_price,
            }) for line in self.sale_id.line_ids]

    def confirm_return(self):
        stock = self.env['gum.stock'].search([], limit=1)
        if not stock:
            stock = self.env['gum.stock'].create({
                'talha_quantity': 0.0,
                'hashab_quantity': 0.0,
                'olibanum_quantity': 0.0,
                'talha_price': 0.0,
                'hashab_price': 0.0,
                'olibanum_price': 0.0
            })

        for line in self.line_ids:
            if line.quantity <= 0:
                raise UserError(f"Return quantity must be greater than zero for {line.gum_type}")

            if line.gum_type == 'talha_gum':
                stock.sudo().write({'talha_quantity': stock.talha_quantity + line.quantity})
            elif line.gum_type == 'hashab_gum':
                stock.sudo().write({'hashab_quantity': stock.hashab_quantity + line.quantity})
            elif line.gum_type == 'olibanum_gum':
                stock.sudo().write({'olibanum_quantity': stock.olibanum_quantity + line.quantity})

            self.message_post(body=f"Returned {line.quantity} of {line.gum_type} added back to stock.")

    @api.model
    def create(self, vals):
        if 'sale_id' in vals and not vals.get('customer_id'):
            sale = self.env['sale'].browse(vals['sale_id'])
            vals['customer_id'] = sale.customer_id.id if sale else False
        res = super(Returns, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('returns_seq')
        return res

    def write(self, vals):
        if 'sale_id' in vals and not vals.get('customer_id'):
            sale = self.env['sale'].browse(vals['sale_id'])
            vals['customer_id'] = sale.customer_id.id if sale else False
        return super(Returns, self).write(vals)


class ReturnsLine(models.Model):
    _name = 'returns.line'
    _description = 'Return Line'

    return_id = fields.Many2one('returns', string="Return Reference", ondelete='cascade')
    sale_line_id = fields.Many2one('sale.line', string="Sale Line")
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum')
    ], string="Gum Type", readonly=True)
    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", readonly=True)

    @api.onchange('sale_line_id')
    def _onchange_sale_line_id(self):
        if self.sale_line_id:
            self.gum_type = self.sale_line_id.gum_type
            self.unit_price = self.sale_line_id.unit_price
            self.quantity = self.sale_line_id.quantity

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'sale_line_id' in vals:
                sale_line = self.env['sale.line'].browse(vals['sale_line_id'])
                vals['unit_price'] = sale_line.unit_price
                vals['gum_type'] = sale_line.gum_type
                vals['quantity'] = sale_line.quantity
        return super(ReturnsLine, self).create(vals_list)

# from odoo import models,fields,api
#
# from odoo17.odoo.exceptions import UserError
#
# class Returns(models.Model):
#     _name = 'returns'
#     _description = 'Returns'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     active = fields.Boolean(default=True)
#     ref = fields.Char(default='New', readonly=True)
#     return_id = fields.Char(string="Return ID", required=True, tracking=True)
#     return_date = fields.Date(string="Return Date", default=fields.Datetime.now, required=True, tracking=True)
#     sale_id = fields.Many2one('sale', string="Sale Reference", required=True, tracking=True)
#     customer_id = fields.Many2one('customer', string="Customer Name", readonly=True)
#     line_ids = fields.One2many('returns.line', 'return_id', string="Return Lines")
#     return_reason_id = fields.Text(string="Return Reason", required=True, tracking=True)
#     @api.onchange('sale_id')
#     def _onchange_sale_id(self):
#         if self.sale_id:
#             self.customer_id = self.sale_id.customer_id.id
#             self.line_ids = [(0, 0, {
#                 'sale_line_id': line.id,
#                 'gum_type': line.gum_type,
#                 'quantity': line.quantity,
#                 'unit_price': line.unit_price,
#             }) for line in self.sale_id.line_ids]
#
#     def confirm_return(self):
#         stock = self.env['gum.stock'].search([], limit=1)
#         if not stock:
#             stock = self.env['gum.stock'].create({
#                 'talha_quantity': 0.0,
#                 'hashab_quantity': 0.0,
#                 'olibanum_quantity': 0.0,
#                 'talha_price': 0.0,
#                 'hashab_price': 0.0,
#                 'olibanum_price': 0.0
#             })
#
#         for line in self.line_ids:
#             if line.quantity <= 0:
#                 raise UserError(f"Return quantity must be greater than zero for {line.gum_type}")
#
#             # تحديث المخزون
#             if line.gum_type == 'talha_gum':
#                 stock.sudo().write({'talha_quantity': stock.talha_quantity + line.quantity})
#             elif line.gum_type == 'hashab_gum':
#                 stock.sudo().write({'hashab_quantity': stock.hashab_quantity + line.quantity})
#             elif line.gum_type == 'olibanum_gum':
#                 stock.sudo().write({'olibanum_quantity': stock.olibanum_quantity + line.quantity})
#
#             # سجل رسالة في chatter
#             self.message_post(body=f"Returned {line.quantity} of {line.gum_type} added back to stock.")
#
#
#     @api.model
#     def create(self, vals):
#         res = super(Returns, self).create(vals)
#         if res.ref == 'New':
#             res.ref = self.env['ir.sequence'].next_by_code('returns_seq')
#         return res
#
#
# class ReturnsLine(models.Model):
#     _name = 'returns.line'
#     _description = 'Return Line'
#
#     return_id = fields.Many2one('returns', string="Return Reference", ondelete='cascade')
#     sale_line_id = fields.Many2one('sale.line', string="Sale Line")
#     gum_type = fields.Selection([
#         ('talha_gum', 'Talha Gum'),
#         ('hashab_gum', 'Hashab Gum'),
#         ('olibanum_gum', 'Olibanum Gum')
#     ], string="Gum Type", readonly=True)
#     quantity = fields.Float(string="Quantity", required=True)
#     unit_price = fields.Float(string="Unit Price", readonly=True)
#
#
#     @api.onchange('sale_line_id')
#     def _onchange_sale_line_id(self):
#         if self.sale_line_id:
#             self.gum_type = self.sale_line_id.gum_type
#             self.unit_price = self.sale_line_id.unit_price
#             self.quantity = self.sale_line_id.quantity
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             if 'sale_line_id' in vals:
#                 sale_line = self.env['sale.line'].browse(vals['sale_line_id'])
#                 vals['unit_price'] = sale_line.unit_price
#                 vals['gum_type'] = sale_line.gum_type
#                 vals['quantity'] = sale_line.quantity
#         return super(ReturnsLine, self).create(vals_list)