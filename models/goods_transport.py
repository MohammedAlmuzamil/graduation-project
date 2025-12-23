from odoo import models,fields,api

class GoodsTransport(models.Model):
    _name = 'goods.transport'
    _description = 'Goods Transport'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    driver_id = fields.Many2one('driver',string = "Driver ID",required = True, tracking = True)
    truck_id = fields.Many2one('trucks',string = "Truck ID",required = True, tracking = True)
    employee_id = fields.Many2one('employee',string="Employee ID",required = True, tracking = True)
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required = True, tracking = True, default = 'talha_gum', string = "Arabic Gum Type")
    gum_qty = fields.Float(string="Gum Quantity",required = True, tracking = True)
    transport_date = fields.Date(string = "Transport Date",default=fields.Datetime.now(),required = True, tracking = True)
    transport_id = fields.Char(string = "Transport ID",required = True, tracking = True)
    warehouse_id = fields.Many2one('warehouse',string="Warehouse ID",required = True, tracking = True)
    state = fields.Selection([
        ('pending','Pending'),
        ('loaded','Loaded'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
    ],default='pending',required = True, tracking = True)
    _sql_constraints = [
        ('unique_id', 'unique("transport_id")', 'This ID Is Exist!')
    ]



    def action_pending(self):
        for rec in self:
            rec.state='pending'




    def action_loaded(self):
        for rec in self:
            rec.state='loaded'




    def action_in_transit(self):
        for rec in self:
            rec.state='in_transit'



    def action_delivered(self):
        for rec in self:
            rec.state = 'delivered'

            last_record = self.env['arabic.gum.type'].search([], order="name desc", limit=1)
            if last_record and last_record.name:
                next_name = last_record.name + 1
            else:
                next_name = 1

            gum_type = self.env['arabic.gum.type'].create({
                'name': next_name,
                'arabic_gum_type': rec.gum_type,
                'quantity': rec.gum_qty,
                'color': 'light_colored',
                'quality': 'good',
            })

            if rec.warehouse_id:
                gum_type.warehouse_ids = [(4, rec.warehouse_id.id)]

    @api.model
    def create(self, vals):
        res = super(GoodsTransport, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('goods_transport_seq')
        return res