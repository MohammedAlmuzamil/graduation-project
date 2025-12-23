from odoo import models,fields,api

class RawStorageReceipt(models.Model):
    _name = 'raw.storage.receipt'
    _description = 'Raw Storage Receipt'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(default='New', readonly=1)
    active = fields.Boolean(default=True)
    receipt_id = fields.Char(string="Receipt ID",required=True,tracking=True)
    warehouse_id = fields.Many2one('warehouse',string="Warehouse ID",required=True,tracking=True)
    employee_id = fields.Many2one('employee',string="Employee",required=True,tracking=True)
    date = fields.Date(string="Date",required=True,default=fields.Datetime.now(),tracking=True)
    received_qty = fields.Float(string="Received Quantity",required=True,tracking=True)

    _sql_constraints = [
        ('unique_id', 'unique("storing_id")', 'This ID Is Exist!')
    ]

    @api.model
    def create(self, vals):
        res = super(RawStorageReceipt, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('raw_storage_receipt_seq')
        return res