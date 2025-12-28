from odoo import models,fields,api

class Job(models.Model):
    _name = 'job'
    _description = 'Job'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)
    ref = fields.Char(default='New', readonly=1,string="Number")
    name = fields.Char(string="Job Name", required=True,tracking=True)
    job_number = fields.Integer(string="Job ID", required=True,tracking=True)
    grade = fields.Char(string="Job Grade",tracking=True)
    employee_ids = fields.One2many('employee','job_id',string="Employee",tracking=True)
    employee_count = fields.Integer(string="Employee Count",compute="_compute_employee_count")

    _sql_constraints = [
        ('unique_id', 'unique("job_number")', 'This ID Is Exist!')
    ]

    def _compute_employee_count(self):
        for rec in self:
            rec.employee_count = len(rec.employee_ids)

    @api.model
    def create(self, vals):
        res = super(Job, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('job_seq')
        return res
