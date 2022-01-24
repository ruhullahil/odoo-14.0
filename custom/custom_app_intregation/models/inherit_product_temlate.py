from odoo import fields, models, api


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    is_battle_include = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Include Bottle')
    discount = fields.Float(string='Discount')


