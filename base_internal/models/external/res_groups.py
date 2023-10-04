from collections import defaultdict

from odoo import _, api, fields, models


class RemoteUserGroup(models.Model):
    _name = 'external.res.groups'
    _description = 'External Access Groups'

    name = fields.Char(string="Name", required=True)
    external_id = fields.Char(string="External ID", required=True, index=True)
    version_ids = fields.Many2many(string="Versions", comodel_name='external.ir.model.version')
    active = fields.Boolean(string="Active", default=True)

    module = fields.Char(string="Module", compute="_compute_external_parts")
    external_name = fields.Char(string="External Name", compute="_compute_external_parts")

    @api.depends('external_id')
    def _compute_external_parts(self):
        for group in self:
            if group.external_id:
                group.module, group.external_name = group.external_id.split('.')
            else:
                group.module, group.external_name = False, False

    @api.model_create_multi
    def create(self, vals_list):
        new_list = []
        groups = self.env['external.res.groups']

        # Pre-search for existing models
        existing_groups = defaultdict(lambda: self.env['external.res.groups'])
        found_groups = groups.with_context(active_test=False).search([('external_id', 'in', [v['external_id'] for v in vals_list if 'external_id' in v])])
        for group in found_groups:
            existing_groups[group.external_id] |= group

        for vals in vals_list:
            # TODO: This can most definitely be optimized to not do a search for every element.
            if (external_id := vals.get('external_id')) and \
                    (group := existing_groups[external_id]):
                group.write(vals)
                groups |= group
            else:
                new_list.append(vals)
        return super().create(new_list) | groups
