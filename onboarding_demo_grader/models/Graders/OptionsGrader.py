from odoo import _, _lt, api, fields, models, tools
from odoo.addons.base_internal.tools import RPC
from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import \
    BaseGrader

TECHNICAL_NAME = 'options'
STRING = "Multiple Options"
HELP_TEXT = _lt("""
For criteria that have multiple solutions, this will allow you set graders for each possible solution.
This grader will then return the highest score of all of the individual graders.
""")

class OptionGrader(BaseGrader):
    def __init__(self, criteria ) -> None:
        super().__init__(criteria)
        self.graders = [{
            'name': c.name,
            'grader': c._get_grader(),
        } for c in criteria.options_sub_criteria_line_ids]

    def grade(self, db: RPC) -> int:
        results = [{
            'name': g['name'],
            **g['grader'].grade(db)
        } for g in self.graders]
        best_result = max(results, key=lambda r: r['score'])
        return {
            'score': best_result['score'],
            'notes': best_result['name']+ '\n' + best_result['notes']
        }


class OptionCriteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})

    options_sub_criteria_line_ids = fields.One2many(string="Options Subcriteria", comodel_name='onboarding.rubric.line', inverse_name='options_parent_criteria_line_id', copy=True)
    options_parent_criteria_line_id = fields.Many2one(string="Options Parent Criteria", comodel_name='onboarding.rubric.line', ondelete='cascade')

    @api.depends('criteria_type')
    def _compute_help_text(self):
        super()._compute_help_text()
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.help_text = HELP_TEXT

    def _get_grader(self):
        self.ensure_one()
        if self.criteria_type == TECHNICAL_NAME:
            return OptionGrader(self)
        return super()._get_grader()

    @api.depends('options_parent_criteria_line_id.max_score')
    def _compute_max_score(self):
        for line in self.filtered(lambda l: l.options_parent_criteria_line_id):
            line.max_score = line.options_parent_criteria_line_id.max_score

    @api.depends('options_parent_criteria_line_id')
    def _compute_allowed_versions(self):
        super()._compute_allowed_versions()
        for line in self:
            line.version_ids = line.version_ids + line.options_parent_criteria_line_id.version_ids
