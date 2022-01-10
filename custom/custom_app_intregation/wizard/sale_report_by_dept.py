from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleReportByDepartment(models.TransientModel):
    _name = 'sale.department.report.wizard'
    _description = 'Description'

    start_date = fields.Date(string='Start Date', default=fields.Date.today())
    end_date = fields.Date(string='End Date', default=fields.Date.today())
    department_id = fields.Many2many('sale.department', 'sale_dept_rel', string='Department')

    def get_pdf_report(self):
        data = self.read()[0]
        return self.env.ref('custom_app_intregation.report_sale_report_by_dept').report_action(self,data=data)


class ReportAgedPartnerBalance(models.AbstractModel):
    _name = 'report.custom_app_intregation.sale_report_department_view'
    _description = 'Sale Report By department'

    def _get_report_values(self, docids, data=None):
        print(data)
        start_date = data['data'].get('start_date')
        end_date = data['data'].get('end_date')
        department_ids = data['data'].get('department_id')







