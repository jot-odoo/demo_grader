from odoo import _, _lt, api, fields, models
from odoo.addons.base_internal.tools import RPC
from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import BaseGrader
from odoo.tools.safe_eval import safe_eval

from .utils import get_by_xmlid
from odoo.osv import expression

TECHNICAL_NAME = 'xid'
STRING = "External ID has Values"
HELP_TEXT = _lt("""
Get a specific record by external id and make sure it satisfies the given domain.
""")

class TemplateGrader(BaseGrader):
    def __init__(self, criteria ) -> None:
        super().__init__(criteria)
        self.model = criteria.xid_model.technical_name
        self.external_id = criteria.xid_external_id
        self.domain = safe_eval(criteria.xid_domain)

    def grade(self, db: RPC) -> int:
        res_id = get_by_xmlid(db, self.external_id, self.model)
        if not res_id:
            return {
                'score': 0,
                'notes': f"External ID {self.external_id} not found."
            }
        record = db[self.model].search_read([('id','=',res_id)], ['display_name'], limit=1)
        record_filtered = db[self.model].search_read(expression.AND([[('id','=',res_id)], self.domain]), ['display_name'], limit=1)

        if record == record_filtered:
            return {
                'score': self.max_score,
                'notes': f"{record[0]['display_name']} matched criteria."
            }
        else:
            return {
                'score': 0,
                'notes': f"{record[0]['display_name']} did not match criteria."
            }


class TemplateCriteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})

    xid_model = fields.Many2one(string="Model", comodel_name='external.ir.model')
    xid_external_id = fields.Char(string="External ID")
    xid_domain = fields.Char(string="Domain", default="[]")

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
