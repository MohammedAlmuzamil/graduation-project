from odoo import models, fields, api
from odoo.exceptions import UserError


class GoodsTransport(models.Model):
    _name = 'goods.transport'
    _description = 'Goods Transport'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=True, string="Number")
    name = fields.Integer(string="Transport ID", required=True, tracking=True)
    truck_id = fields.Many2one('trucks', string="Truck ID", required=True, tracking=True)

    driver_name = fields.Many2one(
        related="truck_id.driver_id",
        string="Driver Name",
        store=True,
        readonly=True
    )


    # employee_id = fields.Many2one('employee', string="Employee ID", required=True, tracking=True)
    transport_date = fields.Date(string="Transport Date", default=fields.Date.today, required=True, tracking=True)
    warehouse_id = fields.Many2one('warehouse', string="Warehouse ID", required=True, tracking=True)


    purchase_id = fields.Many2one(
        'purchase',
        string="Purchase ID",
        required=True,
        tracking=True,
        domain=[('is_transferred', '=', False)]
    )

    line_ids = fields.One2many(
        'goods.transport.line',
        'transport_id',
        string="Transport Lines",
        tracking=True
    )

    total_qty = fields.Float(string="Total Quantity (Kg)", compute="_compute_total_qty", store=True)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ], default='pending', required=True, tracking=True)


    note = fields.Text(string="Note", required=True, tracking=True)

    _sql_constraints = [
        ('unique_transport_id', 'unique("name")', 'This Transport ID already exists!')
    ]



    @api.constrains('name')
    def _check_transport_id_validation(self):
        for rec in self :
            if not rec.name or rec.name <=0 :
                raise UserError("This Transport ID Is Not Valid")

    @api.onchange('purchase_id')
    def _onchange_order_id(self):
        if self.purchase_id:
            self.warehouse_id = self.purchase_id.warehouse_id.id
            self.line_ids = [(5, 0, 0)]
            lines = []
            for line in self.purchase_id.line_ids:
                lines.append((0, 0, {
                    'gum_type': line.gum_type,
                    'gum_qty': line.quantity,
                }))
            self.line_ids = lines

    @api.depends('line_ids.gum_qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(line.gum_qty for line in rec.line_ids)

    def action_pending(self):
        for rec in self:
            rec.state = 'pending'

    def action_loaded(self):
        for rec in self:
            rec.state = 'loaded'

    def action_in_transit(self):
        for rec in self:
            rec.state = 'in_transit'

    def action_delivered(self):
        for rec in self:
            rec.state = 'delivered'
            rec.purchase_id.is_transferred = True

            storage = self.env['raw.storage'].create({
                'name': rec.name,
                'warehouse_id': rec.warehouse_id.id,
                'storing_date': fields.Date.today(),
            })


            for line in rec.line_ids:
                self.env['raw.storage.line'].create({
                    'raw_id': storage.id,
                    'arabic_gum_type': line.gum_type,
                    'quantity': line.gum_qty,
                })

    @api.model
    def create(self, vals):
        res = super(GoodsTransport, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('goods_transport_seq')
        return res


class GoodsTransportLine(models.Model):
    _name = 'goods.transport.line'
    _description = 'Goods Transport Line'

    transport_id = fields.Many2one('goods.transport', string="Transport", ondelete='cascade')
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
    ], required=True, string="Arabic Gum Type")
    gum_qty = fields.Float(string="Quantity (Kg)", required=True)

