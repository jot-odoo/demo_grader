import re

from odoo import _, api, fields, models
from odoo.addons.base_internal.tools import RPC
from odoo.exceptions import UserError


class OnboardingDatabase(models.Model):
    _name = 'onboarding.database'
    _description = "Demo Database"
    _rec_name = 'url'

    user_id = fields.Many2one(string="Employee", comodel_name='res.users', required=True, default=lambda self: self.env.user)

    url = fields.Char(string="URL", required=True)
    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True, default=lambda self: self.env.user.email)
    password = fields.Char(string="API Key")

    version_id = fields.Many2one(string="Version", comodel_name='external.ir.model.version', compute='_compute_version_id', store=True)

    active = fields.Boolean(string="Active", default=True)

    @api.depends('url', 'name')
    def _compute_version_id(self):
        for db in self:
            env = db._connect(raise_no_password_error=False)
            version = env.get_version()
            db.version_id = self.env['external.ir.model.version'].create([{'name': version}])

    @api.model
    def name_create(self, name: str) -> tuple[int, str]:
        if match := re.search("(?:http[s]*\:\/\/)*(.*?)\.(?=[^\/]*\..{2,5})", name):
            return self.create({
                'url': name,
                'name': match.group(1)
            }).name_get()[0]
        return super().name_create(name)

    def _connect(self, raise_no_password_error=True):
        self.ensure_one()
        if not self.password and raise_no_password_error:
            raise UserError(_("No password set for %s" % self.url))
        return RPC(
            url = self.url,
            db = self.name,
            username = self.email,
            password = self.password
        )

