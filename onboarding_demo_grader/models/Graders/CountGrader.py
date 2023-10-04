import operator

from odoo import fields, models, api, _lt
from odoo.addons.base_internal.tools import RPC
from odoo.tools.safe_eval import safe_eval

from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import BaseGrader
import xmlrpc

TECHNICAL_NAME = 'count'
STRING = "Search & Count"
HELP_TEXT = _lt("""
The grader will search for records matching the given domain and compare the number of records found to the given value.
""")

OPS = {
    '=': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
}

class CountGrader(BaseGrader):
    def __init__(self, criteria) -> None:
        super().__init__(criteria)
        self.model_name = criteria.count_model.name
        self.model = criteria.count_model.technical_name
        self.domain = safe_eval(criteria.count_domain)
        self.comparator = criteria.count_comparator
        self.value = criteria.count_value
        self.active_test = not criteria.count_include_archived

    def grade(self, db: RPC) -> int:
        try:
            res = db[self.model].search_read(self.domain, ['display_name'], context={'active_test': self.active_test})
        except xmlrpc.client.Fault as e:
            return {
                'score': 0,
                'notes': f"{e.faultString}"
            }
        res = [f"{r['display_name']}" for r in res]
        count = len(res)
        notes = ""
        if count > 5:
            notes = f"Found {count} {self.model_name}: [{', '.join(map(str,res[:5]))}, ...]"
        elif count == 1:
            notes = f"Found {count} {self.model_name}: {res[0]}"
        else:
            notes = f"Found {count} {self.model_name}: {res}"

        return {
            'score': self.max_score if OPS[self.comparator](len(res), self.value) else 0,
            'notes': notes
        }


class CountCriteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})

    count_model = fields.Many2one(string="Model", comodel_name='external.ir.model')
    count_domain = fields.Char(string="Domain", default="[]")
    count_comparator = fields.Selection(string="Comparator", selection=[('=', '='), ('!=', '!='), ('<', '<'), ('<=', '<='), ('>', '>'), ('>=', '>=')], default='=')
    count_value = fields.Integer(string="Value", default=1)
    
    count_include_archived = fields.Boolean(string="Include Archived Records", default=False)

    @api.depends('criteria_type')
    def _compute_help_text(self):
        super()._compute_help_text()
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.help_text = HELP_TEXT

    def _get_grader(self):
        self.ensure_one()
        if self.criteria_type == TECHNICAL_NAME:
            return CountGrader(self)
        return super()._get_grader()
