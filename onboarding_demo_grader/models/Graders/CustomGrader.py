from odoo import _, api, fields, models, tools, _lt
from odoo.addons.base_internal.tools import RPC
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval, test_python_expr
from pytz import timezone

from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import BaseGrader


TECHNICAL_NAME = 'custom'
STRING = "Custom Code"
HELP_TEXT = _lt("""Run a custom Python script to grade this criteria.""")

DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: External Odoo Environment on database to be graded
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - float_compare: Odoo function to compare floats based on specific precisions
#  - UserError: Warning Exception to use with raise
#  - Warning: Warning Exception to use with raise
# 
# Assign the grade to the grade variable at the end. Leave any notes in the notes variable.
# \n\n\n\n
grade = 0
notes = ""
"""

class CustomGrader(BaseGrader):
    def __init__(self, criteria) -> None:
        super().__init__(criteria)
        self.custom_query = criteria.custom_query

    def _get_eval_context(self, db: RPC):
        return {
            'env': db,
            'time': tools.safe_eval.time,
            'datetime': tools.safe_eval.datetime,
            'dateutil': tools.safe_eval.dateutil,
            'timezone': timezone,
            'float_compare': float_compare,
            'Warning': Warning,
            'UserError': UserError,
        }

    def grade(self, db: RPC) -> int:
        context = self._get_eval_context(db)
        context.update({'grade': 0, 'notes': ''})
        safe_eval(self.custom_query, context, nocopy=True, mode='exec') # Should write to grade
        return {
            'score': min(context.get('grade',0), self.max_score),
            'notes': context.get('notes', '')
        }


class CustomCriteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})


    custom_query = fields.Text(string="Query",default=DEFAULT_PYTHON_CODE,)

    @api.constrains('custom_query')
    def _check_python_code(self):
        for action in self.sudo().filtered('custom_query'):
            msg = test_python_expr(expr=action.custom_query.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    @api.depends('criteria_type')
    def _compute_help_text(self):
        super()._compute_help_text()
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.help_text = HELP_TEXT

    def _get_grader(self):
        self.ensure_one()
        if self.criteria_type == TECHNICAL_NAME:
            return CustomGrader(self)
        return super()._get_grader()