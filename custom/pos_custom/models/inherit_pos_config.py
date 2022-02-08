from odoo import fields, models, api


class InheritPosConfig(models.Model):
    _inherit = 'pos.config'
    _description = 'Description'

    default_location = fields.Many2one('stock.location', related='picking_type_id.default_location_src_id',
                                       string='Default Location')
