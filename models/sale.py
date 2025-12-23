from odoo import models,fields,api

from odoo17.odoo.exceptions import UserError


class Sale(models.Model):
    _name = 'sale'
    _description = 'Sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1, copy=False)
    name = fields.Char(string="Invoice Number", required=True, tracking=True)
    warehouse_id = fields.Many2one('warehouse', string="Warehouse", required=True, tracking=True)
    employee_id = fields.Many2one('employee', string="Employee", required=True, tracking=True)
    customer_id = fields.Many2one('customer', string="Customer", required=True, tracking=True)
    sale_date = fields.Date(string="Sale Date", default=fields.Datetime.now, required=True, tracking=True)

    line_ids = fields.One2many('sale.line', 'sale_id', string="Sale Lines")

    amount_total = fields.Float(string="Total Amount", compute="_compute_amount_total", store=True)

    _sql_constraints = [
        ('unique_invoice', 'unique(name)', 'This Invoice Number already exists!')
    ]



    def action_confirm_sale(self):

        if not self.line_ids:
            raise UserError("You must add at least one Sale Line before confirming.")
        self._compute_amount_total()
        self.message_post(body=f"Sale {self.ref} has been confirmed.")
        return True





    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(line.subtotal for line in rec.line_ids)

    def action_open_related_employee(self):
        action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.employee_action')
        view_id = self.env.ref('boraush_trading.employee_view_form').id
        action['res_id'] = self.employee_id.id
        action['views'] = [[view_id,'form']]
        return action


    def action_open_related_customer(self):
        action = self.env['ir.actions.actions']._for_xml_id('boraush_trading.customer_action')
        view_id = self.env.ref('boraush_trading.customer_view_form').id
        action['res_id'] = self.customer_id.id
        action['views'] = [[view_id,'form']]
        return action

    def action_open_related_warehouse(self):
        action  = self.env['ir.actions.actions']._for_xml_id('boraush_trading.warehouse_action')
        view_id = self.env.ref('boraush_trading.warehouse_view_form').id
        action['res_id'] = self.warehouse_id.id
        action['views'] = [[view_id,'form']]
        return action








    @api.model
    def create(self, vals):
        res = super(Sale, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('sale_seq')
        return res









class SaleLine(models.Model):
    _name = 'sale.line'
    _description = 'Sale Line'

    sale_id = fields.Many2one('sale', string="Sale Order", ondelete='cascade')
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum')
    ], string="Gum Type", required=True)

    quantity = fields.Float(string="Quantity", required=True)
    unit_price = fields.Float(string="Unit Price", compute="_compute_unit_price", store=True, readonly=False)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)





    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.depends('gum_type')
    def _compute_unit_price(self):
        stock = self.env['gum.stock'].search([], limit=1)
        for line in self:
            if line.gum_type == 'talha_gum':
                line.unit_price = stock.talha_price
            elif line.gum_type == 'hashab_gum':
                line.unit_price = stock.hashab_price
            elif line.gum_type == 'olibanum_gum':
                line.unit_price = stock.olibanum_price
            else:
                line.unit_price = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleLine, self).create(vals_list)
        stock = self.env['gum.stock'].search([], limit=1)

        for line in lines:
            if line.gum_type == 'talha_gum':
                if stock.talha_quantity < line.quantity:
                    raise UserError("Not enough Talha Gum in stock!")
                stock.talha_quantity -= line.quantity

            elif line.gum_type == 'hashab_gum':
                if stock.hashab_quantity < line.quantity:
                    raise UserError("Not enough Hashab Gum in stock!")
                stock.hashab_quantity -= line.quantity

            elif line.gum_type == 'olibanum_gum':
                if stock.olibanum_quantity < line.quantity:
                    raise UserError("Not enough Olibanum Gum in stock!")
                stock.olibanum_quantity -= line.quantity

        return lines


