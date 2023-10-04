import re

from odoo import api, fields, models, Command

from ...tools import RPC


class GetExternalSchema(models.TransientModel):
    _name = 'external.get.schema'
    _description = 'Get External Schema Wizard'

    url = fields.Char(string="Runbot URL", required=True)
    database_name = fields.Char(string="Database Name")

    def get_schema(self):
        if match := re.search("(?:http[s]*\:\/\/)*(.*?)\.(?=[^\/]*\..{2,5})", self.url):
            env = RPC(self.url, db=match.group(1), username='admin', password='admin')
        else:
            env = RPC(self.url, db=self.database_name, username='admin', password='admin')

        server_version = self.env['external.ir.model.version'].create({'name': env.common.version()['server_version']})

        # ============== Get Models ==============
        models = env['ir.model'].search_read([('state', '=', 'base'),('transient','=',False),('abstract','=',False)], ['model', 'name'])
        models = self.env['external.ir.model'].create([{
            'name': model['name'],
            'technical_name': model['model'],
            'version_ids': [Command.link(server_version.id)]
        } for model in models])

        # ============== Get Fields ==============
        model_ids = {
            model.technical_name: model.id for model in models
        }
        fields = env['ir.model.fields'].search_read([('state', '=', 'base')], ['model', 'name', 'ttype', 'field_description'])
        self.env['external.ir.model.fields'].create([{
            'name': field['field_description'],
            'technical_name': field['name'],
            'model_id': model_ids[field['model']],
            'ttype': field['ttype'],
            'version_ids': [Command.link(server_version.id)]
        } for field in fields if field['model'] in model_ids])

        # ============== Get Groups ==============
        groups = env['res.groups'].search_read([], ['name','display_name'])
        xml_ids = env['ir.model.data'].search_read([('model', '=', 'res.groups'), ('res_id', 'in', [g['id'] for g in groups])], ['res_id', 'module', 'name'])
        groups = {g['id']: g for g in groups}
        xml_ids = {g['res_id']: f"{g['module']}.{g['name']}" for g in xml_ids}

        self.env['external.res.groups'].create([{ 
            'name': group['display_name'],
            'external_id': xml_ids[group['id']],
            'version_ids': [Command.link(server_version.id)]
        } for group in groups.values() if group['id'] in xml_ids])
        return
