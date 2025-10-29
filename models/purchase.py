from odoo import models,fields,api

from odoo17.odoo.exceptions import UserError
from odoo17.odoo.tools.populate import compute


class Purchase(models.Model):
    _name = 'purchase'
    _description = 'Purchase'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    ref = fields.Char(default='New', readonly=1)
    active = fields.Boolean(default=True)
    purchase_id = fields.Char(string="Purchase ID", required=True, tracking=True, default='New')


    total_price = fields.Float(string="Total Price", compute='_compute_total_price', store=True)

    purchase_date = fields.Date(string="Purchase Date", required=True, tracking=True, default=fields.Datetime.now())

    line_ids = fields.One2many('purchase.line', 'purchase_id', string="Purchase Lines")
    description = fields.Text(string="Note")
    _sql_constraints = [
        ('unique_purchase_id', 'unique(purchase_id)', 'This Purchase ID already exists!')
    ]

    @api.depends('line_ids.total_price')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = sum(line.total_price for line in rec.line_ids)



    @api.model
    def create(self, vals):
        res = super(Purchase, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('purchase_seq')
        return res

    def confirm_purchase(self):
        for purchase in self:
            if not purchase.line_ids:
                raise UserError("No purchase lines found for this purchase.")
            for line in purchase.line_ids:
                if not line.quantity:
                    raise UserError(f"Quantity cannot be empty for line: {line.gum_type}")
                if not line.commissioner_id:
                    raise UserError(f"Commissioner must be set for line: {line.gum_type}")

                last_record = self.env['arabic.gum.type'].search([], order="name desc", limit=1)
                next_name = int(last_record.name) + 1 if last_record else 1

                gum_record = self.env['arabic.gum.type'].create({
                    'name': next_name,
                    'arabic_gum_type': line.gum_type,
                    'quantity': line.quantity,
                    'color': line.color,
                    'quality': line.quality,
                })

                if line.warehouse_id:
                    gum_record.warehouse_ids = [(4, line.warehouse_id.id)]







class PurchaseLine(models.Model):
    _name = 'purchase.line'
    _description = 'Purchase Line'

    purchase_id = fields.Many2one('purchase', string="Purchase Reference", required=True, ondelete='cascade')
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], string="Arabic Gum Type", required=True)

    color = fields.Selection([
        ('light_colored', 'Light Colored'),
        ('dark_colored', 'Dark Colored'),
    ], string="Color", required=True, default='light_colored')

    quality = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor'),
    ], string="Quality", required=True, default='good')


    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", required=True)
    total_price = fields.Float(string="Total Price", compute='_compute_total_price', store=True)
    warehouse_id = fields.Many2one('warehouse', string="Warehouse", required=True)
    commissioner_id = fields.Many2one('commissioner', string="Commissioner", required=True)






    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for line in self:
            line.total_price = line.quantity * line.unit_price