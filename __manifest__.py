{
    'name': 'Real Estate',
    'category': 'Real Estate/Real Estate',
    'description': "",
    'website': 'https://www.odoo.com/page/estate',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_user_view.xml',
        'views/estate_menus.xml',
        'report/estate_property_report.xml',
        'report/report_salesman_properties.xml',

    ],
    'demo': [],
    'css': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}