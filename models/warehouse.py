from odoo import models,fields,api

class Warehouse(models.Model):
    _name = 'warehouse'
    _description = 'Warehouse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref = fields.Char(default='New', readonly=1)
    active = fields.Boolean(default=True)
    name = fields.Char(string="Warehouse Name", required=True, tracking=True)
    warehouse_id = fields.Char(string="Warehouse ID", required=True, tracking=True)
    end_service_date = fields.Date(string="End Service Date", tracking=True, default=fields.Datetime.now())
    arabic_gum = fields.Many2one('arabic.gum', string="Arabic Gum Type")
    stock = fields.Many2one('gum.stock', string="Stock")

    warehouseman_id = fields.Many2one(
        'warehouseman',
        string="Warehouseman",
        tracking=True
    )

    _sql_constraints = [
        ('unique_id', 'unique("warehouse_id")', 'This Warehouse ID already exists!')
    ]

    @api.model
    def create(self, vals):
        res = super(Warehouse, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('warehouse_seq')
        return res


    # def action_open_related_employee(self):
    #     action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.employee_action')
    #     view_id = self.env.ref('boraush_trading.employee_view_form').id
    #     action['res_id'] = self.employee_id.id
    #     action['views'] = [[view_id,'form']]
    #     return action