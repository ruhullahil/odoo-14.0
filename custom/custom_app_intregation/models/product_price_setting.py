from odoo import fields, models, api


class ProductPriceDescription(models.Model):
    _name = 'product.price.setup'
    _description = 'Description'

    @api.onchange('product_id', 'sale_group')
    def get_price(self):
        for rec in self:
            rec.price = rec.product_id.product_tmpl_id.list_price
            # return rec.product_id.product_tmpl_id.list_price

    name = fields.Char()
    product_id = fields.Many2one('product.product', string='Product')
    sale_group = fields.Many2one('sale.department', string='Department')
    price = fields.Float(string='Price', store=True)
