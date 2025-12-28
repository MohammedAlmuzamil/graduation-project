from odoo import models, fields, api
from pkg_resources import require


class PurityStorage(models.Model):
    _name = 'purity.storage'
    _description = 'Purity Storage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string="Storing ID", required=True, tracking=True)

    talling_id = fields.Many2one(
        'inventory.of.tallying.product',
        string="Talling Product  ID",
        required=True,
        tracking=True
    )

    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse",
        tracking=True
    )

    storing_date = fields.Date(string="Storage Date", default=fields.Datetime.now(), required=True, tracking=True)

    line_ids = fields.One2many(
        'purity.storage.line',
        'purity_id',
        string="Purity Storage Line",
        required=True,
        tracking=True
    )

    total_quantity = fields.Float(
        compute="_compute_total",
        store=True
    )
    total_refined_quantity = fields.Float(
        compute="_compute_total_refined",
        store=True
    )

    _sql_constraints = [
        ('unique_id', 'unique("name")', 'This ID Is Exist!')
    ]

    @api.onchange('talling_id')
    def _onchange_talling_id(self):
        if self.talling_id:
            self.line_ids = [(5, 0, 0)]
            for line in self.talling_id.line_ids:
                self.line_ids = [(0, 0, {
                    'arabic_gum_type': line.arabic_gum_type,
                    'net_quantity': line.net_quantity,
                    'refined_quantity': line.refined_quantity,
                })]

    @api.depends('line_ids.net_quantity')
    def _compute_total(self):
        for rec in self:
            rec.total_quantity = sum(line.net_quantity for line in rec.line_ids)




    @api.depends('line_ids.refined_quantity')
    def _compute_total_refined(self):
        for rec in self:
            rec.total_refined_quantity = sum(line.refined_quantity for line in rec.line_ids)


class PurityStorageLine(models.Model):
    _name = 'purity.storage.line'
    _description = 'Purity Storage Line'

    purity_id = fields.Many2one('purity.storage')
    arabic_gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required=True, tracking=True, default='talha_gum', string="Arabic Gum Type")
    net_quantity = fields.Float(string="Quantity After Cleaning", required=True, tracking=True)
    refined_quantity = fields.Float(string="Refined Quantity")
