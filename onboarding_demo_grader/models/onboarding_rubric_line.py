from odoo import _, api, fields, models
from odoo.addons.base_internal.tools import RPC


class BaseGrader(object):
    def __init__(self, criteria) -> None:
        self.criteria = criteria
        self.max_score = criteria.max_score

    def grade(self, db: RPC) -> int:
        return {
            'score': 0,
            'notes': "Manually graded"
        }


class OnboardingCriteria(models.Model):
    _name = 'onboarding.rubric.line'
    _description = "Criteria"
    _order = 'rubric_id, sequence, id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    rubric_id = fields.Many2one(string="Rubric", comodel_name='onboarding.rubric', ondelete='cascade', readonly=True)
    display_type = fields.Selection(string="Display Type", selection=[('line_section', "Section"), ('line_note', "Note")], default=False)
    max_score = fields.Integer(string="Max Score", default=0, compute='_compute_max_score', readonly=False, store=True, recursive=True)

    description = fields.Html(string="Description")
    help_text = fields.Html(string="Help Text", compute='_compute_help_text', default="")
    criteria_type = fields.Selection(string="Criteria Type", selection=[('manual',"Manual Grade")], required=True, default='manual')
    version_ids = fields.Many2many(string="Versions", comodel_name='external.ir.model.version', compute='_compute_allowed_versions')

    @api.depends('rubric_id.version_ids')
    def _compute_allowed_versions(self):
        for line in self:
            line.version_ids = line.rubric_id.version_ids

    def _compute_max_score(self):
        pass

    def _grade(self, database: RPC) -> bool:
        self.ensure_one()
        return self._get_grader().grade(database)

    def _get_demo_line_vals(self):
        vals = []
        for line in self:
            vals.append({
                'rubric_line_id': line.id,
                'name': line.name,
                'sequence': line.sequence,
                'display_type': line.display_type,
                'max_score': line.max_score,
            })
        return vals

    def _get_grader(self):
        self.ensure_one()
        return Grader(self)

    @api.onchange('criteria_type')
    def _compute_help_text(self):
        for line in self.filtered(lambda l: l.criteria_type == 'manual'):
            line.help_text = "This criteria is manually graded."

    def action_open_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("onboarding_demo_grader.onboarding_rubric_line_action")
        action['res_id'] = self.id
        return action