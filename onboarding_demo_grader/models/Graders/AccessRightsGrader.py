import math

from odoo import _, _lt, api, fields, models
from odoo.addons.base_internal.tools import RPC
from odoo.addons.onboarding_demo_grader.models.onboarding_rubric_line import \
    BaseGrader
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from .utils import get_by_xmlids

TECHNICAL_NAME = 'access_rights'
STRING = "Access Rights"
HELP_TEXT = _lt("""
The grader will search for a user matching the given domain and compare their groups to the given groups. They will receive
partial credit based on the number of groups they have that match the included groups and the number of groups they don't
have that match the excluded groups.
""")

class AccessRightsGrader(BaseGrader):
    def __init__(self, criteria) -> None:
        super().__init__(criteria)
        self.user_domain = safe_eval(criteria.access_rights_user_domain)
        self.include_groups = criteria.access_rights_include_groups
        self.exclude_groups = criteria.access_rights_exclude_groups
        self.checks = len(criteria.access_rights_include_groups) + len(criteria.access_rights_exclude_groups)

    def grade(self, db: RPC) -> int:
        """Grab all of the groups and compare them to the user's groups.
        
        This is a workaround because has_group doesn't work over the external API due to a bug.
        So we instead grab all of the groups by their external ids and directly compare them to the user's groups.
        We don't simply search for a user with all of the included groups and none of the excluded groups because
        that would be too strict. We want to be able to give partial credit for partial matches.
        """

        passed_checks = 0
        msgs = []
        
        # Grab the user
        user = db['res.users'].search_read(self.user_domain, ['name','groups_id'], limit=1, order="id asc")
        if not user:
            raise UserError("No user found matching domain.")
        user = user[0]
        msgs.append(f"Found the following user: {user['name']}")

        groups = get_by_xmlids(db, (self.include_groups + self.exclude_groups).mapped('external_id'), 'res.groups')

        # Compare the user's groups to the groups we're looking for
        for group in self.include_groups:
            if groups[group.external_id] in user['groups_id']:
                passed_checks += 1
            else:
                msgs.append(f"User does not have group {group.name} ({group.external_id})")
        for group in self.exclude_groups:
            if groups[group.external_id] not in user['groups_id']:
                passed_checks += 1
            else:
                msgs.append(f"User has group {group.name} ({group.external_id}) but shouldn't.")
        
        if passed_checks == self.checks:
            msgs.append("User passed all checks.")
        
        return {
            'score': math.ceil(passed_checks / self.checks * self.max_score),
            'notes': "\n".join(msgs)
        }


class AccessRightsCriteria(models.Model):
    _inherit = 'onboarding.rubric.line'

    criteria_type = fields.Selection(string="Criteria Type", selection_add=[(TECHNICAL_NAME, STRING)], ondelete={TECHNICAL_NAME: 'cascade',})

    access_rights_user_domain = fields.Char(string="User Domain", default="[]")
    access_rights_include_groups = fields.Many2many(string="Include Groups", comodel_name='external.res.groups', relation='onboarding_rubric_line_access_rights_include_groups_rel')
    access_rights_exclude_groups = fields.Many2many(string="Exclude Groups", comodel_name='external.res.groups', relation='onboarding_rubric_line_access_rights_exclude_groups_rel')
    
    @api.depends('criteria_type')
    def _compute_help_text(self):
        super()._compute_help_text()
        for line in self.filtered(lambda l: l.criteria_type == TECHNICAL_NAME):
            line.help_text = HELP_TEXT

    def _get_grader(self):
        self.ensure_one()
        if self.criteria_type == TECHNICAL_NAME:
            return AccessRightsGrader(self)
        return super()._get_grader()
