from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'res.partner'
    _description = 'Description'

    lat = fields.Float(string='Latitude')
    lon = fields.Float(string='Longitude')
    customer_dept = fields.Many2one('sale.department', string='Sale Department')
