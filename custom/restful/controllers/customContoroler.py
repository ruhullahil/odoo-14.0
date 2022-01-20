import json

from odoo import http
from odoo.addons.restful.controllers.main import validate_token
from odoo.http import request
from datetime import date
from datetime import datetime


class ModelName(http.Controller):

    @http.route(['/api/get_order/'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_order(self):
        values = {}
        user = request.env.user.id
        datas = request.env['sale.order'].sudo().search([("user_id", "=", user)], limit=500, order='id desc')

        if datas:
            values['success'] = True
            order_list = list()
            for data in datas:
                order_line = list()
                for dt in data.order_line:
                    line_temp = {
                        'product': dt.name,
                        'quantity': dt.product_uom_qty,
                        'total': dt.price_subtotal
                    }
                    order_line.append(line_temp)
                temp = {
                    'name': data.name,
                    'id': data.id,
                    'customer': data.partner_id.name,
                    'total': data.amount_total,
                    'order_line': order_line

                }
                order_list.append(temp)
                values['data'] = order_list
        else:
            values['success'] = False
            values['data'] = list()

        return json.dumps(values)

    @http.route(['/api/confirm_order/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_order_confirm(self, id):
        values = {}
        if not id:
            values['success'] = False
            return json.dumps(values)
        order = request.env['sale.order'].sudo().search([('id', '=', id)], limit=1)
        if order.state == 'sale':
            values['success'] = False
            return json.dumps(values)
        order.action_confirm()
        values['success'] = True
        return json.dumps(values)

    @http.route(['/api/get_delivery/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_delivery(self, id):
        values = {}
        domain = list()
        user = request.env.user.id
        if int(id) == 0:
            domain.append('|')
            domain.append(("user_id", "=", user))
            domain.append(('create_uid', '=', user))
        else:
            domain.append(('location_id', '=', id))

        datas = request.env['stock.picking'].sudo().search(domain, limit=500, order='id desc')

        if datas:
            values['success'] = True
            order_list = list()
            for data in datas:
                order_line = list()
                for dt in data.move_ids_without_package:
                    line_temp = {
                        'product': dt.product_id.product_tmpl_id.name,
                        'quantity': dt.product_uom_qty,
                    }
                    order_line.append(line_temp)
                temp = {
                    'name': data.name,
                    'id': data.id,
                    'customer': data.partner_id.name,
                    'order_line': order_line

                }
                order_list.append(temp)
                values['data'] = order_list
        else:
            values['success'] = False
            values['data'] = list()

        return json.dumps(values)

    @http.route(['/api/validate_delivery/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_delever_confirm(self, id):
        values = {}
        if not id:
            values['success'] = False
            return json.dumps(values)
        order = request.env['stock.picking'].sudo().search([('id', '=', id)], limit=1)
        if order.state in ['done', 'cancel']:
            values['success'] = False
            return json.dumps(values)
        if order.state == 'confirmed':
            order.action_assign()
        if order.state == 'confirmed':
            values['success'] = False
            return json.dumps(values)
        if order.state == 'assigned':
            imideate_transfer_ids = [(0, 0, {
                'picking_id': order.id,
                'to_immediate': True
            })]
            emideate_trns = request.env['stock.immediate.transfer'].sudo().create({
                'pick_ids': order.ids,
                'show_transfers': False,
                'immediate_transfer_line_ids': imideate_transfer_ids

            })
            emideate_trns.process()
            # stock_picking.process()
            order.button_validate()
            if order.state == 'done':
                values['success'] = True
            else:
                values['success'] = False
            return json.dumps(values)

    @http.route(['/api/get_stock_quant/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_stock_quant(self, id):
        values = {}
        domain = list()
        stock = request.env['stock.quant'].sudo().search([('location_id', '=', int(id))])
        quant_list = list()
        if not stock:
            values['success'] = False
            return json.dumps(values)
        for q in stock:
            temp = {
                'product': q.product_id.product_tmpl_id.name,
                'product_id': q.product_id.id,
                'quantity': q.quantity,
                'location': q.location_id.name,
            }
            quant_list.append(temp)
        values['success'] = True
        values['data'] = quant_list
        return json.dumps(values)

    @http.route(['/api/get_invoices/'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_invoices(self):
        values = {}
        datas = request.env['account.move'].sudo().search([], limit=700, order='id desc')
        if datas:
            values['success'] = True
            order_list = list()
            for data in datas:
                order_line = list()
                for dt in data.order_line:
                    line_temp = {
                        'product': dt.name,
                        'quantity': dt.quqntity,
                        'total': dt.price_subtotal
                    }
                    order_line.append(line_temp)
                temp = {
                    'name': data.name,
                    'id': data.id,
                    'customer': data.partner_id.name,
                    'total': data.amount_total,
                    'order_line': order_line

                }
                order_list.append(temp)
                values['data'] = order_list
        else:
            values['success'] = False
            values['data'] = list()

        return json.dumps(values)

    @http.route(['/api/create_invoices/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def create_invoices(self, id):
        values = {}
        order = request.env['sale.order'].sudo().search([('id', '=', int(id))])
        invoice_advance = request.env['sale.advance.payment.inv'].sudo().create({
            'advance_payment_method': 'delivered'

        })
        if order.invoice_status == 'to invoice':
            invoice_advance.create_invoices(order.id)
            values['success'] = True
            invoice_lists = list()
            for invoice in order.invoice_ids:
                temp = {
                    'name': invoice.name,
                    'id': invoice.id,
                }
                invoice_lists.append(temp)
            values['data'] = invoice_lists
            return json.dumps(values)
        else:
            values['success'] = False
            invoice_lists = list()
            for invoice in order.invoice_ids:
                temp = {
                    'name': invoice.name,
                    'id': invoice.id,
                }
                invoice_lists.append(temp)
            values['data'] = invoice_lists
            return json.dumps(values)

    @http.route(['/api/confirm_invoices/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def confirm_invoices(self, id):
        values = {}
        if not id:
            values['success'] = False
            return json.dumps(values)
        invoices = request.env['account.move'].sudo().search([('id', '=', int(id))])
        if not invoices:
            values['success'] = False
            return json.dumps(values)
        if invoices.state in ['posted', 'cancel']:
            values['success'] = False
            return json.dumps(values)
        invoices.action_post()
        if invoices.state == 'posted':
            values['success'] = True
            return json.dumps(values)
        else:
            values['success'] = False
            return json.dumps(values)

    @http.route(['/api/get_sales_man_info/'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_sale_man_info(self):
        values = {}
        user = request.env.user.id
        location = request.env['transport.vehicle.register'].sudo().search([('sales_man', '=', user)], limit=1)

        my_date = date.today()
        dates = datetime(my_date.year, my_date.month, my_date.day)
        sale_count = request.env['sale.order'].sudo().search_count(
            [('create_uid', '=', user), ('date_order', '>=', dates)])
        values['success'] = True
        temp = list()
        t = {
            'name': request.env.user.name,
            'location_id': location.related_location.id,
            'location_name': location.name,
            'sale_count': sale_count

        }
        temp.append(t)
        values['data'] = temp
        return json.dumps(values)
