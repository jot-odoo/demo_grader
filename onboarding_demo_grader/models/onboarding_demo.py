from odoo import _, api, fields, models, Command


STATES = {
    'draft': [('readonly', False)],
    'ready': [('readonly', True)],
    'graded': [('readonly', True)],
    'done': [('readonly', True)],
}


class OnboardingDatabaseResult(models.Model):
    _name = 'onboarding.demo'
    _description = "Demo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one(string="Employee", comodel_name='res.users', required=True, default=lambda self: self.env.user, tracking=True, states=STATES)
    grader_ids = fields.Many2many(string="Graders", comodel_name='res.users', tracking=True, states=STATES|{'ready': [('readonly', False)]},
        domain=lambda self: [('groups_id', 'in', self.env.ref('onboarding_demo_grader.onboarding_demo_grader').id)],    
    )
    rubric_id = fields.Many2one(string="Demo", comodel_name='onboarding.rubric', required=True, states=STATES)
    description = fields.Text(string="Description", related='rubric_id.description')

    state = fields.Selection(string="Status", selection=[('draft', "Draft"), ('ready',"Ready"), ('graded', "Graded"), ('done',"Done")], default='draft', tracking=True)
    
    database_id = fields.Many2one(string="Database", comodel_name='onboarding.database', required=True, domain="[('user_id', '=', user_id)]", states=STATES)
    url = fields.Char(related='database_id.url', readonly=False, states=STATES)
    name = fields.Char(related='database_id.name', readonly=False, states=STATES)
    email = fields.Char(related='database_id.email', readonly=False, states=STATES)
    password = fields.Char(related='database_id.password', readonly=False, states=STATES)
    version_id = fields.Many2one(related='database_id.version_id')

    date = fields.Datetime(string="Date", readonly=True)
    score = fields.Integer(string="Score", compute='_compute_score', store=True, tracking=True, readonly=True)
    max_score = fields.Integer(string="Max Score", compute='_compute_score', store=True, readonly=True)
    line_ids = fields.One2many(string="Criteria", comodel_name='onboarding.demo.line', inverse_name='demo_id', states=STATES|{'graded': [('readonly', False)]})

    @api.depends('line_ids.score')
    def _compute_score(self):
        for demo in self:
            demo.score = sum(demo.line_ids.mapped('score'))
            demo.max_score = sum(demo.line_ids.mapped('max_score'))

    def action_ready(self):
        for demo in self:
            demo.state = 'ready'

    def action_grade(self):
        for demo in self:
            demo._copy_from_rubric()
            demo.line_ids.grade()
            demo.state = 'graded'
            demo.date = fields.Datetime.now()

    def _copy_from_rubric(self):
        for demo in self:
            graded_line_vals = [Command.clear()]
            for line in demo.rubric_id.line_ids:
                vals = line._get_demo_line_vals()
                graded_line_vals.extend([Command.create(v) for v in vals])
            demo.line_ids = graded_line_vals

    def action_validate(self):
        for demo in self:
            demo.state = 'done'

    def action_unvalidate(self):
        for demo in self:
            demo.state = 'graded'

    def name_get(self):
        result = []
        for demo in self:
            name = f"{demo.user_id.name} - {demo.rubric_id.name}"
            result.append((demo.id, name))
        return result


class OnboardingDatabaseResult(models.Model):
    _name = 'onboarding.demo.line'
    _description = 'Onboarding Demo Results'
    _order = 'demo_id, sequence, id'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    demo_id = fields.Many2one(string="Demo", comodel_name='onboarding.demo', required=True, ondelete='cascade')
    rubric_line_id = fields.Many2one(string="Criteria", comodel_name='onboarding.rubric.line')
    display_type = fields.Selection(string="Display Type", selection=[('line_section', "Section"), ('line_note', "Note")], default=False)
    max_score = fields.Integer(string="Max Score", default=0, group_operator='sum')
    state = fields.Selection(related='demo_id.state')
    criteria_type = fields.Selection(related='rubric_line_id.criteria_type')

    score = fields.Integer(string="Score", group_operator='sum')
    notes = fields.Text(string="Notes")

    def grade(self):
        for line in self.filtered(lambda l: l.rubric_line_id and not l.display_type):
            db = line.demo_id.database_id._connect()
            line.write(line.rubric_line_id._grade(db))

