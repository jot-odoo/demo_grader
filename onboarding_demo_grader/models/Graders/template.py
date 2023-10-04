from odoo import _, _lt, api, fields, models
from odoo.addons.base_internal.tools import RPC
from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import BaseGrader

TECHNICAL_NAME = 'template'
STRING = "Template"
HELP_TEXT = _lt("""
    This is a template for creating new graders. It is not actually loaded into the database or imported in any way.
    All you have to do to add a new grader is to duplicate this file, add any necessary fields to the model, and
    modify the __init__ and grade methods on the grader class. Then just import the new grader in the __init__.py
    and add a new view to display your new fields.
""")

class Grader(BaseGrader):
    def __init__(self, criteria ) -> None:
        super().__init__(criteria)

    def grade(self, db: RPC) -> int:
        return {
            'score': self.max_score,
            'notes': "Template"
        }


class Criteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})

    @api.depends('criteria_type')
    def _compute_help_text(self):
        super()._compute_help_text()
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.help_text = HELP_TEXT

    def _get_grader(self):
        self.ensure_one()
        if self.criteria_type == TECHNICAL_NAME:
            return Grader(self)
        return super()._get_grader()
