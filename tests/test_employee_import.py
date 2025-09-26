# custom_hr_import_api/tests/test_employee_import.py
from odoo.tests.common import TransactionCase
import base64
from io import BytesIO
from openpyxl import Workbook

class TestEmployeeImport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Job = self.env['employee.import.job']

    def _make_xlsx(self, rows):
        wb = Workbook()
        ws = wb.active
        for r in rows:
            ws.append(r)
        stream = BytesIO()
        wb.save(stream)
        return base64.b64encode(stream.getvalue())

    def test_import_basic(self):
        rows = [
            ['name','work_email','identification_id','work_phone'],
            ['John Doe','john.doe@example.com','ID001','0811000001'],
            ['Jane Doe','jane.doe@example.com','ID002','0811000002'],
        ]
        data = self._make_xlsx(rows)
        job = self.Job.create({'file': data, 'file_name':'test.xlsx'})
        job.process_file()
        self.assertEqual(self.env['hr.employee'].sudo().search_count([('identification_id','in',['ID001','ID002'])]), 2)
