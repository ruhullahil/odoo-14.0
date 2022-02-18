from odoo import fields, models, api


class VehicleUnloadLine(models.Model):
    _name = 'vehicle.unload.line'
    _description = 'Description'
    _rec_name = 'product_id'

    @api.depends('product_id', 'total_count', 'good_condition', 'broken_condition', 'spoil_condition')
    def _get_lost_count(self):
        for rec in self:
            rec.lost_condition = rec.total_count - (rec.spoil_condition + rec.good_condition + rec.broken_condition)

    location = fields.Many2one('stock.location', string='location')
    product_id = fields.Many2one('product.product', string='Products')
    total_count = fields.Float(string='Total')
    good_condition = fields.Float(string='Good', default=0)
    broken_condition = fields.Float(string='Broken', default=0)
    spoil_condition = fields.Float(string='Spoil', default=0)
    lost_condition = fields.Float(string='Lost', compute='_get_lost_count', store=True)
    unload_id = fields.Many2one('vehicle.unload', string='unload id')


class VehicleUnload(models.Model):
    _name = 'vehicle.unload'
    _description = 'Description'

    @api.depends('vehicle_id')
    def _get_location(self):
        for rec in self:
            rec.location_id = rec.vehicle_id.related_location

    name = fields.Char(string='Name')
    vehicle_id = fields.Many2one('transport.vehicle.register', string='Vehicle')
    location_id = fields.Many2one('stock.location', compute='_get_location', store=True)
    unload_line = fields.One2many('vehicle.unload.line', 'unload_id', string='Vehicle Unload line')
    refarence_picking = fields.Many2one('stock.picking', string='Ref')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('need_examined', 'Need Examined'),
        ('passed', 'passed'),
    ], default='draft')

    def create_unload_picking(self):
        get_in_picking_type = self.env['stock.warehouse'].sudo().search([('company_id', '=', self.env.company.id)],
                                                                        limit=1)
        all_stock_picking = self.env['stock.picking'].sudo().search(
            [('location_id', '=', self.location_id.id), ('state', '=', 'assigned')])
        for picking in all_stock_picking:
            picking.do_unreserve()
        stock_moves = list()
        for line in self.unload_line:
            temp = dict()
            temp['product_id'] = line.product_id.id
            temp['name'] = line.product_id.product_tmpl_id.name
            temp['product_uom_qty'] = line.total_count
            temp['product_uom'] = line.product_id.product_tmpl_id.uom_id.id
            stock_moves.append((0, 0, temp))
        stock_picking = self.env['stock.picking'].sudo().create({
            'partner_id': self.env.user.id,
            'picking_type_id': get_in_picking_type.out_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': 5,
            'move_ids_without_package': stock_moves,
        })
        attr = False

        stock_picking.action_confirm()
        stock_picking.action_assign()

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
        return stock_picking

    def unload(self):
        for rec in self:
            rec.state = 'submitted'
            if rec.location_id:
                stocks = self.env['stock.quant'].sudo().search([('location_id', '=', rec.location_id.id)])
                product_line = []
                for stock in stocks:
                    temp = {
                        'location': stock.location_id.id,
                        'product_id': stock.product_id.id,
                        'total_count': stock.quantity
                    }
                    product_line.append((0, 0, temp))
                rec.unload_line = product_line

    def submit(self):
        if not any(line.lost_condition for line in self.unload_line):
            self.refarence_picking = self.create_unload_picking()
            self.state = 'passed'
            return
        self.state = 'need_examined'

    def validate(self):
        self.refarence_picking = self.create_unload_picking()
        self.state = 'passed'

    @api.model
    def create(self, vals_list):
        vals_list['name'] = 'VHU - ' + str(self.search_count([]))
        return super(VehicleUnload, self).create(vals_list)
