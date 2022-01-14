from odoo import fields, models, api
from odoo.exceptions import ValidationError


class VehicleModel(models.Model):
    _name = 'transport.vehicle.register'
    _description = 'Description'

    name = fields.Char(string='VIN', required=True)
    related_location = fields.Many2one('stock.location', string='Related Location')
    related_route = fields.Many2one('stock.location.route', string='Related Route')
    sales_man = fields.Many2one('res.users', string='Sales Man')

    def create_location(self, location_name):
        location = self.env['stock.location'].sudo().search([('name', '=', location_name.lower())], limit=1)
        if not location:
            location = self.env['stock.location'].sudo().create({
                'name': location_name.lower(),
                'location_id': 1,
                'usage': 'internal',
                'is_lorry': True
            })
        return location

    def create_route(self, route_name, location):
        route = self.env['stock.location.route'].sudo().search([('name', '=', route_name.lower())], limit=1)

        if not route:
            company_id = self.env.company.id
            wirehouse = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.env.company.id)],
                                                                  limit=1)
            pick = {
                'name': 'stock to {}'.format(location.name),
                'action': 'pull',
                'picking_type_id': wirehouse.pick_type_id.id,
                'location_src_id': wirehouse.lot_stock_id.id,
                'location_id': location.id,
                'procure_method': 'make_to_stock',
            }
            pack = {
                'name': '{} to Customer'.format(location.name),
                'action': 'pull',
                'picking_type_id': wirehouse.out_type_id.id,
                'location_src_id': location.id,
                'location_id': 5,
                'procure_method': 'make_to_order',
            }
            rules = []
            rules.append((0, 0, pick))
            rules.append((0, 0, pack))
            route = self.env['stock.location.route'].sudo().create({
                'name': route_name.lower(),
                'sequence': 10 + len(route_name),
                'sale_selectable': True,
                'product_selectable': True,
                'rule_ids': rules
            })
        return route

    @api.model
    def create(self, vals_list):
        if 'name' not in vals_list:
            raise ValidationError('Name field Must need to Fill Up')
        name = vals_list['name']
        location = self.create_location(name)
        rute = self.create_route(name, location)
        vals_list['related_location'] = location.id
        vals_list['related_route'] = rute.id
        return super(VehicleModel, self).create(vals_list)
