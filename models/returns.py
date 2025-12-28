from odoo import models, fields, api
from odoo.exceptions import UserError


class Returns(models.Model):
    _name = 'returns'
    _description = 'Returns'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=True)
    name = fields.Integer(string="Return ID", required=True, tracking=True)
    return_date = fields.Date(string="Return Date", default=fields.Date.context_today, required=True, tracking=True)

    sale_id = fields.Many2one(
        'sale',
        string="Sale Order ID",
        required=True,
        tracking=True,
        domain=lambda self: [('id', 'not in', self._get_confirmed_sale_ids())]
    )

    warehouse_id = fields.Many2one(
        'warehouse',
        string="Warehouse",
        required=True,
        tracking=True
    )
    customer_id = fields.Many2one(
        'customer',
        string="Customer Name"
    )

    return_reason = fields.Many2one(
        'return.reason',
        string="Return Reason",
        required=True,
        tracking=True
    )

    line_ids = fields.One2many(
        'returns.line',
        'return_id',
        string="Return Lines"
    )
    amount_total = fields.Float(
        string="Total Amount",
        compute="_compute_amount_total",
        store=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)


    _sql_constraints = [
        ('unique_return_id', 'unique(name)', 'This Return ID already exists!')
    ]



    @api.model
    def _get_confirmed_sale_ids(self):
        confirmed_returns = self.env['returns'].search([('state', '=', 'confirmed')])
        return confirmed_returns.mapped('sale_id').ids

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(line.subtotal for line in rec.line_ids)

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        if self.sale_id:
            self.customer_id = self.sale_id.customer_id
            self.warehouse_id = self.sale_id.warehouse_id
            self.line_ids = [(5, 0, 0)]
            lines = []
            for line in self.sale_id.line_ids:
                lines.append((0, 0, {
                    'sale_line_id': line.id,
                    'gum_type': line.gum_type,
                    'quantity': line.quantity,
                    'unit_price': line.unit_price,
                }))
            if lines:
                self.line_ids = lines

    def action_confirm(self):
        for rec in self:
            existing = self.search([
                ('sale_id', '=', rec.sale_id.id),
                ('state', '=', 'confirmed')
            ], limit=1)
            if existing and existing.id != rec.id:
                raise UserError(f"A confirmed return already exists for this sale ({existing.name}).")

            if not rec.line_ids:
                raise UserError("No return lines found.")



            Stock = self.env['gum.stock'].sudo()
            stock = Stock.search([], limit=1)
            if not stock:
                stock = Stock.create({
                    'talha_quantity': 0.0,
                    'hashab_quantity': 0.0,
                    'olibanum_quantity': 0.0,
                    'refined_quantity': 0.0,
                })

            talha_delta = hashab_delta = olibanum_delta = refined_delta = 0.0

            for line in rec.line_ids:
                qty = float(line.quantity or 0.0)
                if qty <= 0:
                    raise UserError(f"Return quantity must be greater than zero for {line.gum_type}")
                if line.gum_type == 'talha_gum':
                    talha_delta += qty
                elif line.gum_type == 'hashab_gum':
                    hashab_delta += qty
                elif line.gum_type == 'olibanum_gum':
                    olibanum_delta += qty
                elif line.gum_type == 'refined_gum':
                    refined_delta += qty

            stock.write({
                'talha_quantity': (stock.talha_quantity or 0.0) + talha_delta,
                'hashab_quantity': (stock.hashab_quantity or 0.0) + hashab_delta,
                'olibanum_quantity': (stock.olibanum_quantity or 0.0) + olibanum_delta,
                'refined_quantity': (stock.refined_quantity or 0.0) + refined_delta,
                'update_date': fields.Date.context_today(self),
            })

            if rec.sale_id.check_returned != 'returned':
                rec.sale_id.write({'check_returned': 'returned'})

            rec.state = 'confirmed'
            rec.message_post(
                body=f"Return {rec.name or rec.ref} confirmed, stock updated, and Sale marked as returned.")


    @api.model
    def create(self, vals):
        sale_id = vals.get('sale_id')
        if sale_id:
            existing_return = self.search([
                ('sale_id', '=', sale_id),
                ('state', '=', 'confirmed')
            ], limit=1)
            if existing_return:
                raise UserError(f"This sale already has a confirmed return ({existing_return.name}).")

        if sale_id and not vals.get('line_ids'):
            sale = self.env['sale'].browse(sale_id)
            if sale:
                line_vals = []
                for line in sale.line_ids:
                    line_vals.append((0, 0, {
                        'sale_line_id': line.id,
                        'gum_type': line.gum_type,
                        'quantity': line.quantity,
                        'unit_price': line.unit_price,
                    }))
                vals['line_ids'] = line_vals

        res = super(Returns, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('returns_seq') or res.ref
        return res

    def write(self, vals):
        if 'sale_id' in vals and self.state == 'confirmed':
            raise UserError("You cannot change the sale reference after confirming the return.")
        if 'sale_id' in vals and not vals.get('customer_id'):
            sale = self.env['sale'].browse(vals['sale_id'])
            vals['customer_id'] = sale.customer_id.id if sale else False
        return super(Returns, self).write(vals)


class ReturnsLine(models.Model):
    _name = 'returns.line'
    _description = 'Return Line'

    return_id = fields.Many2one('returns', string="Return Reference", ondelete='cascade')
    sale_line_id = fields.Many2one('sale.line', string="Sale Line")
    gum_type = fields.Selection([
        ('talha_gum', 'Talha Gum'),
        ('hashab_gum', 'Hashab Gum'),
        ('olibanum_gum', 'Olibanum Gum'),
        ('refined_gum', 'Refined Gum')
    ], string="Gum Type")

    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0) * (line.unit_price or 0.0)

    @api.onchange('sale_line_id')
    def _onchange_sale_line_id(self):
        if self.sale_line_id:
            self.gum_type = self.sale_line_id.gum_type
            self.unit_price = self.sale_line_id.unit_price
            self.quantity = self.sale_line_id.quantity

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'sale_line_id' in vals:
                sale_line = self.env['sale.line'].browse(vals['sale_line_id'])
                vals['unit_price'] = sale_line.unit_price
                vals['gum_type'] = sale_line.gum_type
                vals['quantity'] = sale_line.quantity
        return super(ReturnsLine, self).create(vals_list)
