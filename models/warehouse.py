from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Warehouse(models.Model):
    _name = 'warehouse'
    _description = 'Warehouse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref = fields.Char(default='New', readonly=1, string="Number")
    active = fields.Boolean(default=True)
    name = fields.Char(string="Warehouse Name", required=True, tracking=True)
    warehouse_id = fields.Integer(string="Warehouse ID", required=True, tracking=True)
    end_service_date = fields.Date(string="End Service Date", tracking=True, default=fields.Datetime.now())
    stock = fields.Many2one(
        'gum.stock',
        string="Stock"
    )
    address_id = fields.Text(string="Address", required=True, tracking=True)

    warehouseman_id = fields.Many2one(
        'warehouseman',
        string="Warehouseman",
        compute='_compute_warehouseman',
        store=True,
        tracking=True
    )

    _sql_constraints = [
        ('unique_id', 'unique("warehouse_id")', 'This Warehouse ID already exists!')
    ]

    @api.constrains('warehouse_id')
    def _check_warehouse_id_validity(self):
        for rec in self:
            if not rec.warehouse_id or rec.warehouse_id <= 0:
                raise ValidationError("This Warehouse ID Is Not Valid")

    @api.constrains('end_service_date')
    def _check_end_service_date_validity(self):
        for rec in self:
            if rec.end_service_date <= date.today():
                raise ValidationError("Warehouseman His Service Period Has Ended")

    @api.depends('warehouseman_id')
    def _compute_warehouseman(self):
        for warehouse in self:
            warehouseman = self.env['warehouseman'].search([('warehouse_id', '=', warehouse.id)], limit=1)
            warehouse.warehouseman_id = warehouseman.id if warehouseman else False
            warehouse.warehouseman_date = warehouseman.create_date if warehouseman else False

    @api.model
    def create(self, vals):
        res = super(Warehouse, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('warehouse_seq')
        return res

    def action_open_related_employee(self):
        action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.employee_action')
        view_id = self.env.ref('boraush_trading.employee_view_form').id
        action['res_id'] = self.warehouseman_id.name.id
        action['views'] = [[view_id, 'form']]
        return action
