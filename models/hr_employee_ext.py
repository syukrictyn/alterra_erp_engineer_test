from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    identification_id = fields.Char(string='Identification')
