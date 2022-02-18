from odoo import fields, models, api
from odoo.exceptions import ValidationError


class VehicleCurrentStock(models.TransientModel):
    _name = 'vehicle.current.stock'
    _description = 'Description'

    name = fields.Many2one('transport.vehicle.register', string='Vehicle')

    # def get_data(self, vehicle):
    #     if not vehicle:
    #         raise ValidationError('please insert vehicle !!!')
    #     location = vehicle.related_location
    #
    #     products_qty = self.env['stock.quant'].sudo().search([('location_id', '=', location.id)])
    #     return {
    #         'vehicle': vehicle,
    #         'sales_man': vehicle.sales_man.name,
    #         'vehicle_name': vehicle.name,
    #         'location': location,
    #         'products_qty': products_qty,
    #     }

    def print_pdf(self):
        for rec in self:
            # data = rec.get_data(rec.name)
            data = self.read()[0]
            return self.env.ref('custom_app_intregation.report_current_stock_report').report_action(self, data=data)


class CurrentStockReportView(models.AbstractModel):
    _name = 'report.custom_app_intregation.report_current_stock_view'
    _description = 'Sale Report By department'

    def get_data(self, vehicle):
        if not vehicle:
            raise ValidationError('please insert vehicle !!!')
        location = vehicle.related_location

        products_qty = self.env['stock.quant'].sudo().search([('location_id', '=', location.id)])
        return {
            'vehicle': vehicle,
            'sales_man': vehicle.sales_man.name,
            'vehicle_name': vehicle.name,
            'location': location,
            'products_qty': products_qty,
        }

    def _get_report_values(self, docids, data=None):
        v_id = data['name'][0]
        vehicle = self.env['transport.vehicle.register'].sudo().search([('id', '=', v_id)], limit=1)
        datas = self.get_data(vehicle)

        return {
            'docs': docids,
            'data': datas,
        }
        # start_date = data['data'].get('start_date')
        # end_date = data['data'].get('end_date')
        # department_ids = data['data'].get('department_id')
