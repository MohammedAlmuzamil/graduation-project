from odoo import models, fields

class SaleAnalysisWizard(models.TransientModel):
    _name = 'sale.analysis.wizard'
    _description = 'Sale Analysis Wizard'

    analysis_text = fields.Html("AI Analysis", readonly=True)
