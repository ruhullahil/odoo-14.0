from odoo import fields, models, api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Description'

    name = fields.Char()
