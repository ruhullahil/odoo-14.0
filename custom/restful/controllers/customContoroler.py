import json

from odoo import http
from odoo.addons.restful.controllers.main import validate_token
from odoo.http import request
from datetime import date
from datetime import datetime


class ModelName(http.Controller):

    @http.route(['/api/get_order/', '/api/get_order/<id>'], type="http", auth="none", website=True, method=['GET'],
                csrf=False)
    @validate_token
    def get_order(self, id=None):
        values = {}
        domain = list()
        user = request.env.user.id
        if id:
            domain.append(("id", "=", id))
        else:
            domain.append(("user_id", "=", user))
        datas = request.env['sale.order'].sudo().search(domain, limit=500, order='id desc')

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
                picking_ids = list()
                for line in data.picking_ids:
                    picking_temp = {
                        'delever_id': line.id,
                        'status': line.state,
                        'dest_id': line.location_dest_id.id,
                    }
                    picking_ids.append(picking_temp)
                temp = {
                    'name': data.name,
                    'id': data.id,
                    'customer': data.partner_id.name,
                    'total': data.amount_total,
                    'order_line': order_line,
                    'picking_line': picking_ids

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

    @http.route(['/api/get_delivery/<id>', '/api/get_delivery/'], type="http", auth="none", website=True,
                method=['GET'],
                csrf=False)
    @validate_token
    def get_delivery(self, id=None):
        values = {}
        domain = list()
        user = request.env.user.id
        if not id:
            domain.append('|')
            domain.append(("user_id", "=", user))
            domain.append(('create_uid', '=', user))
            so_ids = request.env['sale.order'].sudo().search(domain).ids
            domain = [('sale_id', 'in', so_ids), ('state', 'not in', ['done', 'cancel'])]

        else:
            domain.append(('id', '=', id))

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
                    'sale_id': data.sale_id.id,
                    'sale_order': data.sale_id.name,
                    'customer': data.partner_id.name,
                    'order_line': order_line,

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
                self.create_invoices(order.sale_id.id)
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

    @http.route(['/api/get_invoices/', '/api/get_invoices/<id>'], type="http", auth="none", website=True,
                method=['GET'],
                csrf=False)
    @validate_token
    def get_invoices(self, id=None):
        values = {}
        domain = list()
        domain.append(('move_type', '=', 'out_invoice'))
        if id:
            domain.append(('id', '=', id))
        datas = request.env['account.move'].sudo().search(domain, limit=700, order='id desc')
        if datas:
            values['success'] = True
            order_list = list()
            for data in datas:
                order_line = list()
                for dt in data.invoice_line_ids:
                    line_temp = {
                        'product': dt.name,
                        'quantity': dt.quantity,
                        'total': dt.price_subtotal
                    }
                    order_line.append(line_temp)
                temp = {
                    'name': data.name,
                    'id': data.id,
                    'customer': data.partner_id.name,
                    'sale_order': data.invoice_origin if data.invoice_origin else None,
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
            'location_id': location.related_location.id if location else 0,
            'location_name': location.name if location else None,
            'sale_count': sale_count,
            'is_direct_sale': location.enable_direct_sale,
            'direct_route': location.direct_route.id if location.direct_route.id else 0

        }
        temp.append(t)
        values['data'] = temp
        return json.dumps(values)

    @http.route(['/api/create_sale_order/'], type="json", auth="none", website=False, method=['POST'],
                csrf=False)
    @validate_token
    def create_sale_order(self, **payload):
        values = {}
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        order_dict = dict()
        for key, value in payload.items():
            temp_list = list()
            if not value:
                continue
            if isinstance(value, dict):
                temp_list.append((0, 0, value))
            if isinstance(value, list):
                temp = dict()
                for val in value:
                    for inner_key, inn_value in val.items():
                        if not inn_value:
                            continue
                        temp[inner_key] = inn_value
                    temp_list.append((0, 0, temp))
            order_dict[key] = temp_list if temp_list else value
        order = request.env['sale.order'].sudo().create(order_dict)
        if order:
            values['success'] = True
            # value['data'] = {
            #     'order_id': order.id,
            #     'order_name': order.name,
            #     'customer_id': order.partner_id.id,
            #     'customer_name': order.partner_id.name
            # }
            return json.dumps(values)

    @http.route(['/api/create_payment_order/'], type="json", auth="none", website=False, method=['POST'],
                csrf=False)
    @validate_token
    def create_payment(self, **payload):
        values = {}
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        order_dict = dict()
        for key, value in payload.items():
            temp_list = list()
            if isinstance(value, dict):
                temp_list.append((0, 0, value))
            if isinstance(value, list):
                for val in value:
                    temp_list.append((0, 0, val))
            order_dict[key] = temp_list if temp_list else value
        order = request.env['account.payment'].sudo().create(order_dict)
        if order:
            order.action_post()
            values['success'] = True
            values['data'] = {
                'order_id': order.id,
                'order_name': order.name,
                'customer_id': order.partner_id.id,
                'customer_name': order.partner_id.name
            }
            return json.dumps(values)

    @http.route(['/api/get_customer/', '/api/get_customer/<id>'], type="http", auth="none", website=True,
                method=['GET'],
                csrf=False)
    @validate_token
    def get_customer(self, id=None):
        values = {}
        domain = list()
        if id:
            domain.append(('id', '=', id))
        partners = request.env['res.partner'].sudo().search(domain, limit=500, order='id desc')
        if not partners:
            values['success'] = False
            return json.dumps(values)
        partners_lst = list()
        for line in partners:
            temp = {
                'id': line.id,
                'name': line.name,
                'address': str(line.street) + ' ' + str(line.state_id.name),
                'phone_number': line.phone,
                'customer_dept': line.customer_dept.id if line.customer_dept else None
            }
            partners_lst.append(temp)
        values['success'] = True
        values['data'] = partners_lst
        return json.dumps(values)

    @http.route(['/api/create_customer/'], type="json", auth="none", website=False, method=['POST'],
                csrf=False)
    @validate_token
    def create_customer(self, **payload):
        values = {}
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        data = request.env['res.partner'].sudo().create(payload)
        if data:
            values['success'] = True

        return json.dumps(values)

    @http.route(['/api/get_product/', '/api/get_product/<id>'], type="http", auth="none", website=True,
                method=['GET'],
                csrf=False)
    @validate_token
    def get_products(self, id=None):
        values = dict()
        values['success'] = False
        domain = list()
        if id:
            domain.append(('id', '=', id))
        products = request.env['product.product'].sudo().search(domain, limit=600, order='id desc')
        product_list = []
        if products:
            for product in products:
                temp = dict()
                temp['product_id'] = product.id
                temp['product_tmpl_id'] = product.product_tmpl_id.id
                temp['name'] = product.product_tmpl_id.name
                temp['unit_price'] = product.product_tmpl_id.lst_price
                temp['include_bottle'] = product.product_tmpl_id.is_battle_include
                temp['discount'] = product.product_tmpl_id.discount
                base_url = request.env['ir.config_parameter'].get_param('web.base.url')
                temp['img'] = base_url + '/web/image?model=product.template&id={}&field=image_1024'.format(
                    product.product_tmpl_id.id)
                product_list.append(temp)
            values['success'] = True
            values['data'] = product_list
        return json.dumps(values)

    @http.route(['/api/get_product_price_setup/', '/api/get_product_price_setup/<id>'], type="http", auth="none",
                website=True,
                method=['GET'],
                csrf=False)
    @validate_token
    def get_product_price_setup(self, id=None):
        values = {}
        values['success'] = False
        domain = list()
        if id:
            domain.append(('product_id', '=', int(id)))
        setups = request.env['product.price.setup'].sudo().search(domain)
        setup_list = list()
        if setups:
            for setup in setups:
                temp = {
                    'product_id': setup.product_id.id,
                    'dept_id': setup.sale_group.id,
                    'price': setup.price,
                }
                setup_list.append(temp)
            values['data'] = setup_list
        return json.dumps(values)

    @http.route(['/api/get_delivery_from_so/<id>', ], type="http", auth="none",
                website=True,
                method=['GET'],
                csrf=False)
    @validate_token
    def get_delivery_from_so(self, id=None):
        values = {}
        domain = []
        domain.append(('sale_id', '=', int(id)))
        datas = request.env['stock.picking'].sudo().search(domain, limit=3, order='id desc')
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
                    'sale_id': data.sale_id.id,
                    'sale_order': data.sale_id.name,
                    'customer': data.partner_id.name,
                    'order_line': order_line,

                }
                order_list.append(temp)
                values['data'] = order_list
        else:
            values['success'] = False
            values['data'] = list()

        return json.dumps(values)
