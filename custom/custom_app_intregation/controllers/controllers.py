# -*- coding: utf-8 -*-
# from odoo import http


# class CustomAppIntregation(http.Controller):
#     @http.route('/custom_app_intregation/custom_app_intregation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_app_intregation/custom_app_intregation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_app_intregation.listing', {
#             'root': '/custom_app_intregation/custom_app_intregation',
#             'objects': http.request.env['custom_app_intregation.custom_app_intregation'].search([]),
#         })

#     @http.route('/custom_app_intregation/custom_app_intregation/objects/<model("custom_app_intregation.custom_app_intregation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_app_intregation.object', {
#             'object': obj
#         })
