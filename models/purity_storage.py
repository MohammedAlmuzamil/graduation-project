from odoo import models,fields
from pkg_resources import require


class PurityStorage(models.Model):
    _name = 'purity.storage'
    _description = 'Purity Storage'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    warehouse_id = fields.Many2one('warehouse',string="Warehouse",required=True,tracking=True)
    employee_id = fields.Many2one('employee',string="Employee",required = True, tracking = True)
    storing_date = fields.Date(string = "Storage Date",default=fields.Datetime.now(),required = True, tracking = True)
    received_qty = fields.Float(string = "Received Quantity",required = True, tracking = True)
