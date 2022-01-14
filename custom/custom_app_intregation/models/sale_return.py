from odoo import fields, models, api


class CustomerProductReturn(models.Model):
    _name = 'customer.product.return'
    _description = 'Description'

    name = fields.Char()
    customer_id = fields.Many2one('res.partner', string='Customer')
    return_order_line = fields.One2many('customer.product.return.line', 'return_id', string='Return Order Line')
    location_id = fields.Many2one('stock.location', 'Vehicle')
    status = fields.Selection([('draft', 'Initial'), ('done', 'Posted')], default='draft')

    @api.model
    def create(self, vals_list):
        vals_list['name'] = "RET" + str(self.search_count([]) + 1)
        return super(CustomerProductReturn, self).create(vals_list)

    def done_button(self):
        get_in_picking_type = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.env.company.id)],
                                                                        limit=1)
        stock_moves = list()
        for line in self.return_order_line:
            temp = dict()
            temp['product_id'] = line.product_id.id
            temp['name'] = line.product_id.product_tmpl_id.name
            temp['product_uom_qty'] = line.quantity
            temp['product_uom'] = line.product_id.product_tmpl_id.uom_id.id
            stock_moves.append((0, 0, temp))
        stock_picking = self.env['stock.picking'].sudo().create({
            'partner_id': self.customer_id.id,
            'picking_type_id': get_in_picking_type.in_type_id.id,
            'location_id': 5,
            'location_dest_id': self.location_id.id if self.location_id else get_in_picking_type.in_type_id.default_location_dest_id.id,
            'move_ids_without_package': stock_moves,
        })
        attr = False
        stock_picking.action_confirm()
        imideate_transfer_ids = [(0, 0, {
            'picking_id': stock_picking.id,
            'to_immediate': True
        })]
        emideate_trns = self.env['stock.immediate.transfer'].sudo().create({
            'pick_ids': stock_picking.ids,
            'show_transfers': False,
            'immediate_transfer_line_ids': imideate_transfer_ids

        })
        emideate_trns.process()
        # stock_picking.process()
        stock_picking.button_validate()
        if stock_picking.state == 'done':
            invoice_line_ids = list()
            for line in self.return_order_line:
                temp = dict()
                temp['product_id'] = line.product_id.id
                temp['quantity'] = line.product_id.id
                temp['price_unit'] = line.price
                invoice_line_ids.append((0, 0, temp))
            attr = self.env['account.move'].sudo().create({
                'move_type': 'out_refund',
                'partner_id': self.customer_id.id,
                'invoice_date': fields.datetime.now(),
                'invoice_line_ids': invoice_line_ids,

            })
            attr.action_post()
        if attr.state == 'posted' and stock_picking.state=='done' and self.status == 'draft':
            self.status = 'done'
        # stock_picking =


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

    @api.depends('return_id.customer_id')
    def get_default_product(self):
        for rec in self:
            order_line = self.env['sale.order.line'].sudo().search(
                [('order_partner_id', '=', rec.return_id.customer_id.id)])
            list_line = list()
            for line in order_line:
                list_line.append(line.product_id.id)
            products = self.env['product.product'].sudo().search([('id', 'in', list_line)])
            rec.default_product_id = products

    @api.onchange('product_id')
    def _get_default_product(self):
        for rec in self:
            return {
                'domain': {
                    'product_id': [('id', 'in', rec.default_product_id.ids)]
                }
            }

    default_product_id = fields.Many2many('product.product', compute='get_default_product')
    product_id = fields.Many2one('product.product', string='Product', )
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    return_id = fields.Many2one('customer.product.return', string='Return')
