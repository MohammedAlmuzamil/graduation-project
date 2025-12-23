from odoo import models,fields,api

class PureStore(models.Model):
    _name = 'pure.store'
    _description = 'Pure Store'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    # state = fields.Selection([
    #     ('draft','Draft'),
    #     ('received','Received'),
    #     ('verified','Verified'),
    #     ('cancelled','Cancelled'),
    # ])

    ref = fields.Char(default='New', readonly=1)
    purity_type = fields.Char(string = "Purity Type",required = True, tracking = True)
    # purity_id = fields.Many2one('pure',string="Purity ID",required=True,tracking=True)
    commissioner_id = fields.Many2one('commissioner',string="Commissioner ID",required=True,tracking=True)
    warehouse_id = fields.Many2one('warehouse',string="Warehouse ID",required=True,tracking=True)
    quantity = fields.Float(string = "Quantity",required = True, tracking = True)
    receive_date = fields.Date(string = "Received Date",default=fields.Datetime.now(),required = True, tracking = True)
    employee_id = fields.Many2one('employee', string="Employee ID",required=True,tracking=True)
    # unit_price = fields.Float()
    # order_date = fields.Date()

    # _sql_constraints = [
    #     ('unique_id', 'unique("purity_id")', 'This ID Is Exist!')
    # ]

    @api.model
    def create(self, vals):
        res = super(PureStore, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('pure_store_seq')
        return res
    # def action_draft(self):
    #     for rec in self:
    #         rec.state='draft'
    #
    # def action_received(self):
    #     for rec in self:
    #         rec.state='received'
    #
    # def action_verified(self):
    #     for rec in self:
    #         rec.state='verified'
    #
    # def action_cancelled(self):
    #     for rec in self:
    #         rec.state='cancelled'