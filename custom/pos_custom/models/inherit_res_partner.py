from odoo import fields, models, api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Description'

    @api.depends('pos_credit_amount')
    def _get_pos_credit(self):
        for rec in self:
            SQL = """select sum(amount) from pos_payment pp
                left join pos_order poo on pp.pos_order_id = poo.id
                left join pos_payment_method ppm on pp.payment_method_id = ppm.id
                where ppm.id = %s and poo.partner_id = %s"""
            self._cr.execute(SQL, (3, rec.id))
            total_credit = self.env.cr.fetchall()
            self._cr.execute(SQL, (4, rec.id))
            total_debit = self.env.cr.fetchall()
            # print(total_debit,total_credit)
            rec.pos_credit_amount = float(total_credit[0][0] if total_credit[0][0] else 0) - float(total_debit[0][0] if total_debit[0][0] else 0)

    pos_credit_limit = fields.Float(string='Pos Credit Limit')
    pos_credit_amount = fields.Float(compute="_get_pos_credit", string='Pos Credit', store=True)
    is_active = fields.Boolean(string='Active')
    is_over_limit = fields.Boolean(string='Over Limit')
