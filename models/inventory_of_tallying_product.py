from odoo import models, fields, api
from odoo.exceptions import UserError


class InventoryOfTallyingProduct(models.Model):
    _name = 'inventory.of.tallying.product'
    _description = 'Inventory Of Tallying Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1, copy=False, string="Number")
    name = fields.Integer(string="Talling Product ID", required=True, tracking=True)
    product_id = (fields.Many2one
        (
        'raw.storage',
        string="Arabic Gum ID",
        required=True,
        tracking=True,
        domain=[('is_cleaned', '=', False)]
    ))

    date = fields.Date(string="Cleaning Date", required=True, tracking=True, default=fields.Date.context_today)
    description = fields.Text(string="Note", required=True, tracking=True)

    line_ids = fields.One2many(
        'inventory.of.tallying.product.line',
        'tallying_id',
        string="Cleaning Details"
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cleaned', 'Cleaned')
    ], string="Status", default='draft', tracking=True)

    total_refined_quantity = fields.Float(
        compute="_compute_total_refined_quantity",
        string="Total Refined Quantity"
    )

    supervisor_id = fields.Many2one('supervisor',string="Supervisor Name", required=True, tracking=True)
    warehouse_id = fields.Many2one('warehouse', string="Warehouse", required=True, tracking=True)


    _sql_constraints = [
        ('unique_talling_product_id', 'unique("name")', 'This Talling Product ID Is  Already Exists!')
    ]


    @api.constrains('name')
    def _check_talling_product_id_validty(self):
        for rec in self:
            if not rec.name or rec.name <=0 :
                raise UserError("This Talling Product ID Is Not Valid")





    @api.depends('line_ids.refined_quantity')
    def _compute_total_refined_quantity(self):
        for rec in self:
            rec.total_refined_quantity = sum(line.refined_quantity for line in rec.line_ids)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.line_ids = [(5, 0, 0)]
            lines = []
            for line in self.product_id.line_ids:
                lines.append((0, 0, {
                    'arabic_gum_type': line.arabic_gum_type,
                    'quantity': line.quantity,
                }))
            if lines:
                self.line_ids = lines

    def action_view_gum_stock(self):
        stock = self.env['gum.stock'].search([], limit=1)
        if not stock:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Gum Stock',
                'res_model': 'gum.stock',
                'view_mode': 'form',
                'view_id': False,
                'target': 'current',
                'res_id': False,
                'context': {'default_talha_quantity': 0.0, 'default_hashab_quantity': 0.0,
                            'default_olibanum_quantity': 0.0,'default_refined_quantity': 0.0},
            }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gum Stock',
            'res_model': 'gum.stock',
            'view_mode': 'form',
            'res_id': stock.id,
            'target': 'current',
        }





    def action_cleaned(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError("No lines to clean.")

            rec.product_id.is_cleaned = True
            rec.state = 'cleaned'

            purity_storage = self.env['purity.storage'].create({
                'talling_id': rec.id,
                'name': rec.product_id.name,
                'storing_date': fields.Date.today(),
                'warehouse_id': False,
            })

            for line in rec.line_ids:
                self.env['purity.storage.line'].create({
                    'purity_id': purity_storage.id,
                    'arabic_gum_type': line.arabic_gum_type,
                    'net_quantity': line.net_quantity,
                    'refined_quantity': line.refined_quantity,
                })

            stock = self.env['gum.stock'].search([], limit=1)
            if not stock:
                stock = self.env['gum.stock'].create({
                    'talha_quantity': 0.0,
                    'hashab_quantity': 0.0,
                    'olibanum_quantity': 0.0,
                    'refined_quantity': 0.0,
                    'update_date': fields.Date.today(),
                })

            for line in rec.line_ids:
                if line.arabic_gum_type == 'talha_gum':
                    stock.talha_quantity += line.net_quantity
                elif line.arabic_gum_type == 'hashab_gum':
                    stock.hashab_quantity += line.net_quantity
                elif line.arabic_gum_type == 'olibanum_gum':
                    stock.olibanum_quantity += line.net_quantity

                stock.refined_quantity += line.refined_quantity

            stock.update_date = fields.Date.today()

    @api.model
    def create(self, vals):
        res = super(InventoryOfTallyingProduct, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('inventory_of_talling_product_seq')
        return res





class InventoryOfTallyingProductLine(models.Model):
    _name = 'inventory.of.tallying.product.line'
    _description = 'Inventory Of Tallying Product Line'

    tallying_id = fields.Many2one('inventory.of.tallying.product')
    arabic_gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required=True, tracking=True, default='talha_gum', string="Arabic Gum Type")
    quantity = fields.Float(string="Original Quantity", required=True, tracking=True)
    net_quantity = fields.Float(string="Quantity After Cleaning")
    refined_quantity = fields.Float(compute='_compute_refined_quantity', string="Residue Quantity")


    @api.depends('quantity', 'net_quantity')
    def _compute_refined_quantity(self):
        for rec in self:
            rec.refined_quantity = rec.quantity - rec.net_quantity

    @api.constrains('quantity','net_quantity')
    def _check_quantity_grater_than_new_quantity(self):
        for rec in self :
            if rec.net_quantity >= rec.quantity:
                raise UserError("Quantity After Cleaning Cant Exceed Original Quantity")
            elif rec.net_quantity <=0 :
                raise UserError("Quantity After Cleaning Cant Zero Or Negative Number")
