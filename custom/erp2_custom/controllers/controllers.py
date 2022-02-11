# -*- coding: utf-8 -*-
# from odoo import http


# class Erp2Custom(http.Controller):
#     @http.route('/erp2_custom/erp2_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/erp2_custom/erp2_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('erp2_custom.listing', {
#             'root': '/erp2_custom/erp2_custom',
#             'objects': http.request.env['erp2_custom.erp2_custom'].search([]),
#         })

#     @http.route('/erp2_custom/erp2_custom/objects/<model("erp2_custom.erp2_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('erp2_custom.object', {
#             'object': obj
#         })
