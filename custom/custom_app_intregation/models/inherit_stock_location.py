from odoo import fields, models, api


class InheritStockLocation(models.Model):
    _inherit = 'stock.location'
    _description = 'Description'

    is_lorry = fields.Boolean(default=False, string='Lorry')
