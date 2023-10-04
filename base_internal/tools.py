import xmlrpc.client
from functools import partial

from odoo import _
from odoo.exceptions import UserError


class RPC:
    def __init__(self, url, db, username, password, model=None, uid=None) -> None:
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        if model:
            self.model_name = model
        if uid:
            self.uid = uid
        if self.password and not uid:
            self.authenticate()

    def authenticate(self):
        try:
            if uid := self.common.authenticate(self.db, self.username, self.password, {}):
                self.uid = uid
            else:
                raise UserError(_("Cannot connect to the database! Check your login credentials."))
        except UserError:
            raise
        except Exception as e:
            if e.errno == 111:
                raise UserError(_("Cannot connect to the database! Is it running?"))
            raise

    def get_version(self):
        return self.common.version()['server_version']

    def model(self, model):
        return RPC(self.url, self.db, self.username, self.password, model=model, uid=self.uid)

    def __call__(self, method, *args, **kwds):
        if not self.uid:
            self.authenticate()
        return self.models.execute_kw(self.db, self.uid, self.password, self.model_name, method, args, kwds)

    def __getitem__(self, indices):
        return self.model(indices)

    def __getattr__(self, name):
        return partial(self, name)
