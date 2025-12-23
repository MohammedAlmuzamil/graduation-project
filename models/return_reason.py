from odoo import models,fields

class ReturnReason(models.Model):
    _name = 'return.reason'
    _description = 'Return Reason'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    return_date = fields.Date(string = "Return Date", required = True, tracking = True,default = fields.Datetime.now())
    order_id = fields.Many2one('order',string="Order ID",required = True, tracking = True)
    return_reason = fields.Text(string="Return Reason",required = True, tracking = True)