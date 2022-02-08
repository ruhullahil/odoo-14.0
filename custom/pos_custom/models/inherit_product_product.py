from odoo import fields, models, api


class InheritProductProducxt(models.Model):
    _inherit = 'product.product'
    _description = 'Description'
    @api.model
    def get_product_qty_location(self, location):
        print("***")
        return self.with_context(location=location).qty_available
