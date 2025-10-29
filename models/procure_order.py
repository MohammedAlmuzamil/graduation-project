from odoo import models,fields,api



class ProcureOrder(models.Model):
    _name = 'procure.order'
    _description='Procure Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1)
    gum_id = fields.Many2one('arabic.gum.type',string="Gum ID",tracking=True,required=True)
    # quality = fields.Selection([
    #     ('excellent','Excellent'),
    #     ('very_good','Very Good'),
    #     ('good','Good'),
    #     ('average','Average'),
    #     ('poor','Poor'),
    # ])
    quality = fields.Selection(related='gum_id.quality')
    quantity = fields.Float()
    unit_price = fields.Float(related='gum_price_id.unit_price',string="Unit Price",readonly=0)
    # unit_price = fields.Float(string="Unit Price",readonly=0)
    # order_id = fields.Char()
    commissioner_id = fields.Many2one('commissioner')
    gum_price_id = fields.Many2one('arabic.gum.price')

    order_id = fields.Char(string = "Order ID", required = True, tracking = True)
    date = fields.Date(string = "Date", required = True, tracking = True, default = fields.Datetime.now())



    @api.onchange('gum_id')
    def _onchange_gum_id(self):
        if self.gum_id:

            price_record = self.env['arabic.gum.price'].search(
                [('arabic_gum_id', '=', self.gum_id.id)],
                order='price_date desc',
                limit=1
            )
            if price_record:
                self.gum_price_id = price_record.id
                self.unit_price = price_record.unit_price
            else:
                self.gum_price_id = False
                self.unit_price = 0.0

    @api.model
    def create(self, vals):
        res = super(ProcureOrder, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('procure_order_seq')
        return res