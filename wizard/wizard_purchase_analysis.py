from odoo import models, fields

class PurchaseAnalysisWizard(models.TransientModel):
    _name = 'purchase.analysis.wizard'
    _description = 'Purchase Analysis Wizard'

    analysis_text = fields.Html("AI Analysis", readonly=True)
