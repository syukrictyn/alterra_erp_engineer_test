# custom_hr_import_api/__manifest__.py
{
    "name": "Custom HR Import & Invoice API",
    "version": "1.0.0",
    "summary": "Import employees (xlsx) async + Invoice REST API",
    "category": "Human Resources",
    "author": "Syukri Cetyana",
    "license": "LGPL-3",
    "depends": ["base", "hr", "account", "mail", "queue_job" ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/employee_import_views.xml",
        # "data/cron_jobs.xml"
    ],
    "installable": True,
    "application": False,
}
