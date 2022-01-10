from odoo import fields, models, api


class SaleDepartment(models.Model):
    _name = 'sale.department'
    _description = 'Description'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
