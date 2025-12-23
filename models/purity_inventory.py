from odoo import models,fields,api

class PurityInventory(models.Model):
    _name = 'purity.inventory'
    _description = 'Purity Inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    purity_type = fields.Selection([
        ('high','High'),
        ('medium','Medium'),
    ],default='medium',string = "Purity Type", required = True, tracking = True)
    purity_qty = fields.Float(related='pure_id.quantity',string = "Purity Quantity", tracking = True)
    warehouse_id = fields.Many2one(related='pure_id.warehouse_id', string = "Warehouse", required = True, tracking = True)
    date = fields.Date(string = "Date",default=fields.Datetime.now(),required = True, tracking = True)
    pure_id = fields.Many2one('pure',string="Pure ID")

    @api.model
    def create(self, vals):
        res = super(PurityInventory, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('purity_inventory_seq')
        return res