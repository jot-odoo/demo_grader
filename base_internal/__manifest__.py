{
    'name': "Odoo Internal",
    'summary': """Base module for internal Odoo modules""",
    'description': """
Odoo Internal
=============

1) Provides a simple library that provides access to simple xmlrpc util for easily accessing our internal database or other databases.
2) Adds some pseudo-models to store data about the structure of the external database. Mainly just models and fields that we don't want
actually installed on this database.
        """,
    'author': "Odoo Inc",
    'developers': ["John Truong (jot)"],
    'website': "https://www.odoo.com/",
    'category': "Internal",
    'version': "1.0",
'license': "OPL-1",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/external/ir_model.xml',
        'views/external/res_groups.xml',
        'views/external/menuitems.xml',
        'wizards/GetExternalSchema/get_external_schema.xml'
    ],    
    'assets': {
        'web.assets_backend': [
            'base_internal/static/src/**/*.js',
            'base_internal/static/src/**/*.xml',
        ],
    },
    'application': False,
}
