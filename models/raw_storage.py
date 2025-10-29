from odoo import models,fields

class RawStorage(models.Model):
    _name = 'raw.storage'
    _description = 'Raw Storage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    storing_id = fields.Char(string="Storing ID",required=True,tracking=True)
    warehouse_id = fields.Many2one('warehouse',string="Warehouse ID",required=True,tracking=True)
    employee_id = fields.Many2one('employee',string="Employee",required=True,tracking=True)
    storing_date = fields.Date(string="Storing Date",required=True,default=fields.Datetime.now(),tracking=True)
    received_qty = fields.Float(string="Received Quantity",required=True,tracking=True)

    _sql_constraints = [
        ('unique_id', 'unique("storing_id")', 'This ID Is Exist!')
    ]
