{
    'name': "Odoo Internal: Onboarding Demo Grader",
    'summary': """Automatically grade demos for onboarding""",
    'description': """
Odoo Internal: Onboarding Demo Grader
=====================================

Allows the onboarder to set grading criteria for a demo, and then automatically
grade each new hire's demo based on the criteria.
        """,
    'author': "Odoo Inc",
    'developers': ["John Truong (jot)"],
    'website': "https://www.odoo.com/",
    'category': "Internal/Onboarding",
    'version': "1.0",
    'license': "OPL-1",
    'depends': ['mail', 'base_internal', 'web_section_and_note'],
    'data': [
        'security/user_groups.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',
        'views/onboarding_demo_views.xml',
        'views/onboarding_database_views.xml',
        'views/onboarding_rubric_views.xml',
        'views/menuitems.xml',
        # Grader Views
        'views/Graders/Count.xml',
        'views/Graders/Custom.xml',
        'views/Graders/XID.xml',
        'views/Graders/AccessRights.xml',
        'views/Graders/Options.xml',
        'views/Graders/Multipart.xml',
    ],
    # 'demo': [],
    'application': True,
}
