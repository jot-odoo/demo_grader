{
    'name': "Section and Note Widget",
    'summary': """Section and Note widget""",
    'description': """
Section and Note Widget
=======================

Section and Note widget extracted from the account module
so we can use it elsewhere without depending on account.
        """,
    'author': "Odoo Inc",
    'developers': ["John Truong (jot)"],
    'task_ids': [],
    'website': "https://www.odoo.com/",
    'category': "Custom Development",
    'version': "1.0",
    'license': "OPL-1",
    'depends': ['web'],
    'data': [
    ],
    'demo': [],
    'application': False,
    'assets': {
        'web.assets_backend': [
            'web_section_and_note/static/src/components/**/*.js',
            'web_section_and_note/static/src/components/**/*.xml',
            'web_section_and_note/static/src/components/**/*.scss',
        ],
    },
}
