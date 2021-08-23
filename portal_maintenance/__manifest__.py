# -*- coding: utf-8 -*-

{
    'name': 'Portal Maintenance',
    'version': '1.0',
    'author': "Rozy Consultant.",
    'category': 'HR',
    'depends': ['maintenance','portal'],
    'description': """ Maintenance request from portal side""",
    "data": [
        'security/ir.model.access.csv',
        'views/maintenance.xml',
        'views/maintenance_form_view.xml',
    ],
    # 'images': ['static/description/main_screen.png'],
    'currency': 'EUR',
    'price': 150,
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
