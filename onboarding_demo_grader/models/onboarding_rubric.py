from odoo import _, api, fields, models
from odoo.addons.base_internal.tools import RPC


class OnboardingDemo(models.Model):
    _name = 'onboarding.rubric'
    _description = "Rubric"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    version_ids = fields.Many2many(string="Versions", comodel_name='external.ir.model.version')
    description = fields.Text(string="Description")
    line_ids = fields.One2many(string="Criteria", comodel_name='onboarding.rubric.line', inverse_name='rubric_id', copy=True)
    active = fields.Boolean(string="Active", default=True)

    max_score = fields.Integer(string="Max Score", compute='_compute_max_score')

    @api.depends('line_ids.max_score')
    def _compute_max_score(self):
        for demo in self:
            demo.max_score = sum(demo.line_ids.mapped('max_score'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % (self.name)
        return super().copy(default=default)
