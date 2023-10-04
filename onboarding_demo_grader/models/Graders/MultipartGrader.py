from odoo import _, api, fields, models, tools, _lt
from odoo.addons.base_internal.tools import RPC
from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import \
    BaseGrader

TECHNICAL_NAME = 'multipart'
STRING = "Multipart"
HELP_TEXT = _lt("""
Allows you to create a criteria that is graded with multiple criteria. The score returned 
will be the sum of the scores of all of the graders.
""")

class TemplateGrader(BaseGrader):
    def __init__(self, criteria) -> None:
        super().__init__(criteria)
        self.graders = [{
            'name': c.name,
            'grader': c._get_grader(),
        } for c in criteria.multipart_sub_criteria_line_ids]

    def grade(self, db: RPC) -> int:
        results = [{
            'name': g['name'],
            **g['grader'].grade(db)
        } for g in self.graders]
        return {
            'score': sum(r['score'] for r in results),
            'notes': '\n\n'.join(r['name']+ '\n' + r['notes'] for r in results)
        }


class TemplateCriteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})

    multipart_sub_criteria_line_ids = fields.One2many(string="Multipart Sub Criteria", comodel_name='onboarding.rubric.line', inverse_name='multipart_parent_criteria_line_id', copy=True)
    multipart_parent_criteria_line_id = fields.Many2one(string="Multipart Parent Criteria", comodel_name='onboarding.rubric.line', ondelete='cascade')

    @api.depends('criteria_type')
    def _compute_help_text(self):
        super()._compute_help_text()
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.help_text = HELP_TEXT

    def _get_grader(self):
        self.ensure_one()
        if self.criteria_type == TECHNICAL_NAME:
            return TemplateGrader(self)
        return super()._get_grader()

    @api.depends('multipart_sub_criteria_line_ids.max_score')
    def _compute_max_score(self):
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.max_score = sum(c.max_score for c in line.multipart_sub_criteria_line_ids)

    @api.depends('multipart_parent_criteria_line_id')
    def _compute_allowed_versions(self):
        super()._compute_allowed_versions()
        for line in self:
            line.version_ids = line.version_ids + line.multipart_parent_criteria_line_id.version_ids
