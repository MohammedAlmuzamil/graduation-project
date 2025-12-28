from odoo import models,fields,api

class RawStorage(models.Model):
    _name = 'raw.storage'
    _description = 'Raw Storage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(string="Storing ID",required=True,tracking=True)
    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse ID",
        required=True,
        tracking=True
    )

    storing_date = fields.Date(string="Storing Date",required=True,default=fields.Datetime.now(),tracking=True)
    line_ids = fields.One2many(
        'raw.storage.line',
        'raw_id'
    )
    total_quantity = fields.Float(
        compute="_compute_total",
        string="Total Quantity",
        required=True,
        tracking=True
    )
    is_cleaned = fields.Boolean(string="Cleaned", default=False)

    _sql_constraints = [
        ('unique_id', 'unique("storing_id")', 'This ID Is Exist!')
    ]

    @api.depends('line_ids.quantity')
    def _compute_total(self):
        for rec in self:
            rec.total_quantity = sum(line.quantity for line in rec.line_ids)




class RawStorageLine(models.Model):
    _name = 'raw.storage.line'
    _description = 'Raw Storage'
    raw_id = fields.Many2one('raw.storage')
    arabic_gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required=True, tracking=True, default='talha_gum', string="Arabic Gum Type")
    quantity = fields.Float(string="Quantity", required=True, tracking=True)