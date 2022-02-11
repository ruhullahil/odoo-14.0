from odoo import fields, models, api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Description'

    brn_no = fields.Char(string='BRN')
    region = fields.Char(string='Region')
    segment_id = fields.Many2one('partner.segment', string='Segment')
    sub_segment = fields.Many2one('partner.sub.segment', string='Sub Segment', domain="[('segment','=',segment_id)]")


class SegmentPartner(models.Model):
    _name = 'partner.segment'
    _description = "Segment"

    name = fields.Char('Segment')
    sub_segment = fields.One2many('partner.sub.segment', 'segment', string='SubSegment')


class SubSegmentPartner(models.Model):
    _name = 'partner.sub.segment'
    _description = 'SubSegment'

    name = fields.Char(string='Subsegment')
    segment = fields.Many2one('partner.segment', string='segment')
