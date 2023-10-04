from collections import defaultdict

from odoo import _, api, fields, models
from odoo.addons.base.models.ir_model import FIELD_TYPES
from odoo.osv import expression


class RemoteModel(models.Model):
    _name = 'external.ir.model'
    _description = 'External Model'

    name = fields.Char(string="Name", required=True)
    technical_name = fields.Char(string="Technical Name", required=True, index=True)
    field_ids = fields.One2many(string="Fields", comodel_name='external.ir.model.fields', inverse_name='model_id')
    version_ids = fields.Many2many(string="Versions", comodel_name='external.ir.model.version')
    active = fields.Boolean(string="Active", default=True)

    @api.model_create_multi
    def create(self, vals_list):
        new_list = []
        models = self.env['external.ir.model']

        # Pre-search for existing models
        existing_models = defaultdict(lambda: self.env['external.ir.model'])
        found_models = models.with_context(active_test=False).search([('technical_name', 'in', [v['technical_name'] for v in vals_list if 'technical_name' in v])])
        for model in found_models:
            existing_models[model.technical_name] |= model

        for vals in vals_list:
            if (technical_name := vals.get('technical_name')) and \
                    (model := existing_models[technical_name]):
                model.write(vals)
                models |= model
            else:
                new_list.append(vals)
        return super().create(new_list) | models

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('technical_name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self): 
        if not self.user_has_groups('base.group_no_one'):
            return super().name_get()
        names = []
        for model in self:
            names.append((model.id, f"{model.name} ({model.technical_name})"))
        return names


class RemoteField(models.Model):
    _name = 'external.ir.model.fields'
    _description = 'External Fields'

    name = fields.Char(string="Name", required=True)
    technical_name = fields.Char(string="Technical Name", required=True, index=True)
    model_id = fields.Many2one(string="Model", comodel_name='external.ir.model', required=True, ondelete='cascade', index=True)
    version_ids = fields.Many2many(string="Versions", comodel_name='external.ir.model.version')
    active = fields.Boolean(string="Active", default=True)
    ttype = fields.Selection(selection=FIELD_TYPES, string='Field Type', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        new_list = []
        fields = self.env['external.ir.model.fields']

        # Pre-search for existing models
        existing_fields = defaultdict(lambda: self.env['external.ir.model.fields'])
        found_fields = fields.with_context(active_test=False).search([('technical_name', 'in', [v['technical_name'] for v in vals_list if 'technical_name' in v]), ('model_id', 'in', [v['model_id'] for v in vals_list if 'model_id' in v])])
        for field in found_fields:
            existing_fields[(field.technical_name, field.model_id)] |= field

        for vals in vals_list:
            if (technical_name := vals.get('technical_name')) and \
                    (model_id := vals.get('model_id')) and \
                    (field := existing_fields[(technical_name, model_id)]):
                field.write(vals)
                fields |= field
            else:
                new_list.append(vals)
        return super().create(new_list) | fields

class DatabaseVersion(models.Model):
    _name = 'external.ir.model.version'
    _description = 'External Database Version'

    name = fields.Char(string="Name", required=True)

    @api.model_create_multi
    def create(self, vals_list):
        new_list = []
        versions = self.env['external.ir.model.version']
        for vals in vals_list:
            if (name := vals.get('name')) and \
                    (version := versions.with_context(active_test=False).search([('name', '=', name)], limit=1)):
                versions |= version
            else:
                new_list.append(vals)
        return super().create(new_list) | versions
