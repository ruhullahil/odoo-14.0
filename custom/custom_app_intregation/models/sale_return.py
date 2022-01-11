from odoo import fields, models, api


class CustomerProductReturn(models.Model):
    _name = 'customer.product.return'
    _description = 'Description'

    name = fields.Char()
    customer_id = fields.Many2one('res.partner', string='Customer')
    return_order_line = fields.One2many('customer.product.return.line', 'return_id', string='Return Order Line')


class CustomerProductLine(models.Model):
    _name = 'customer.product.return.line'
    _description = 'CustomerProductLine'

    @api.onchange('product_id')
    def _get_product_qty_price(self):
        for rec in self:
            order_line = self.env['sale.order.line'].sudo().search(
                [('product_id', '=', rec.product_id.id), ('order_partner_id', '=', rec.return_id.customer_id.id)],
                limit=1, order='id desc')
            rec.price = order_line.price_unit
            rec.quantity = order_line.product_uom_qty

    def get_default_product(self):
        for rec in self:
            order_line = self.env['sale.order.line'].sudo().search(
                [('order_partner_id', '=', rec.return_id.customer_id.id)])
            list_line = list()
            for line in order_line:
                list_line.append(line.product_id)
            rec.default_product_id = list_line

    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    return_id = fields.Many2one('customer.product.return', string='Return')
    default_product_id = fields.Many2many('product.product', compute='get_default_product')
