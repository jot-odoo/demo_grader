from odoo.osv import expression


def get_by_xmlid(db, xid, model=None):
    module, name = xid.split('.')
    domain = [('module','=',module),('name','=',name)]
    if model:
        domain.append(('model','=',model))
    if record := db['ir.model.data'].search_read(domain, ['res_id'], limit=1):
        return record[0]['res_id']
    else:
        return None

def get_by_xmlids(db, xids, model=None):
    domain = expression.OR(
        [ [('module','=',xid.split('.')[0]),('name','=',xid.split('.')[1])] for xid in xids]
    )
    if model:
        domain = expression.AND([domain, [('model','=',model)]])
    results = db['ir.model.data'].search_read(domain, ['res_id','complete_name'])
    return {r['complete_name']: r['res_id'] for r in results}
