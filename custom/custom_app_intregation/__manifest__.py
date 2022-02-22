# -*- coding: utf-8 -*-
{
    'name': "custom_app_intregation",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', 'stock', 'purchase', 'point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/sale_dept.xml',
        'views/product_price_setting.xml',
        'views/inherit_sale_order.xml',
        'views/res_partner.xml',
        'views/customer_product_return.xml',
        'views/vehicle_setup.xml',
        'views/inherit_product_template.xml',
        'views/vehicle_unload.xml',
        # 'wizard/sale_report_by_dept.xml',
        # 'reports/sale_report_by_dept.xml',
        'reports/current_stock_report.xml',
        'wizard/current_stock_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
