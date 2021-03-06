from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Description'

    department_id = fields.Many2one('sale.department', string='Department')
    vehicle_id = fields.Many2one('transport.vehicle.register', string='Vehicle No.')
    po_id = fields.Many2one('purchase.order', string='P. O. Number')

    @api.onchange('department_id')
    def _get_price_on_change(self):
        # print('***')
        for rec in self:
            print('rec : ', rec)
            # rec.order_line = None
            for line in rec.order_line:
                line.price_unit = line.get_price_list_on_product()
                # line.write({'price_unit': line.get_price_list_on_product()})

    @api.onchange('vehicle_id')
    def _change_vehicle_wise_route(self):
        for rec in self:
            # print('rec : ', rec)
            # rec.order_line = None
            for line in rec.order_line:
                line.route_id = self.vehicle_id.direct_route if self.vehicle_id.enable_direct_sale else self.vehicle_id.related_route.id

    @api.onchange('partner_id')
    def _change_dept(self):
        for rec in self:
            rec.department_id = rec.partner_id.customer_dept

    @api.model
    def create(self, vals):
        if 'department_id' not in vals:
            vals['department_id'] = self.env['res.partner'].sudo().search([('id', '=', vals['partner_id'])],
                                                                          limit=1).customer_dept.id
        return super(SaleOrder, self).create(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_price_list_on_product(self):
        for rec in self:
            price_list = self.env['product.price.setup'].sudo().search(
                [('product_id', '=', rec.product_id.id), ('sale_group', '=', rec.order_id.department_id.id)], limit=1,
                order='id desc').price
            if not price_list:
                price_list = rec.product_id.product_tmpl_id.list_price
            return price_list

    def get_discount(self):
        for rec in self:
            price_list = self.env['product.price.setup'].sudo().search(
                [('product_id', '=', rec.product_id.id), ('sale_group', '=', rec.order_id.department_id.id)], limit=1,
                order='id desc').parcent
            if not price_list:
                price_list = rec.product_id.product_tmpl_id.discount

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.get_price_list_on_product()
            self.route_id = self.order_id.vehicle_id.direct_route if self.order_id.vehicle_id.enable_direct_sale else self.order_id.vehicle_id.related_route.id
            self.discount = self.get_discount()
            # self.price_unit = 5
