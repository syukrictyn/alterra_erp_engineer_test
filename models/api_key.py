# custom_hr_import_api/models/api_key.py
from odoo import models, fields
import secrets

class ApiKey(models.Model):
    _name = 'api.key'
    _description = 'API Key'

    name = fields.Char(required=True)
    key = fields.Char(required=True, readonly=True, default=lambda self: secrets.token_urlsafe(32))
    user_id = fields.Many2one('res.users', string='User', required=True)
    active = fields.Boolean(default=True)
    create_date = fields.Datetime(readonly=True)
