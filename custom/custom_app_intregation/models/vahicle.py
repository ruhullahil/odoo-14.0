from odoo import fields, models, api


class VehicleModel(models.Model):
    _name = 'transport.vehicle.register'
    _description = 'Description'

    name = fields.Char(string='VIN')


