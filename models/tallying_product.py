from odoo import models,fields,api

from odoo17.odoo.exceptions import ValidationError, UserError


class TallyingProduct(models.Model):
    _name = 'tallying.product'
    _description = 'Tallying Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    name = fields.Char(string = "Product Name", required = True, tracking = True)
    product_id = fields.Char(string = "Product ID", required = True, tracking = True)
    product_weight = fields.Float(string = "Product Weight KG", required = True, tracking = True)
    supervisor_id = fields.Many2one('employee',string = "Supervisor ID", required = True, tracking = True)
    warehouse_id = fields.Many2one('warehouse',string = "Warehouse ID", required = True, tracking = True)
    extracted_date = fields.Date(string = "Extracted Date", required = True, tracking = True,default=fields.Datetime.now())
    extracted_qty = fields.Float(string = "Extracted Quantity KG", required = True, tracking = True)


    @api.constrains('product_weight', 'extracted_qty')
    def _check_extracted_qty_greater_than_zero(self):
        for rec in self:
            if rec.product_weight <= 0:
                raise UserError("Product weight must be greater than zero.")

            if rec.extracted_qty <= 0:
                raise UserError("Extracted quantity must be greater than zero.")

            if rec.extracted_qty > rec.product_weight:
                raise UserError("Extracted quantity cannot exceed product weight.")







    @api.model
    def create(self, vals):
        res = super(TallyingProduct, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('tallying_product_seq')
        return res