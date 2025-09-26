# alterra_erp_engineer_test

Import employees (xlsx) async + Invoice REST API  

## Modul: custom_hr_import_api

Modul Odoo 18 untuk:
- Import karyawan dari XLSX secara asinkron (queue/cron)
- API untuk pembuatan invoice dan registrasi pembayaran

## Instalasi singkat (Docker)
1. Copy modul ke folder `./custom_hr_import_api`.
2. Jalankan:
   ```bash
   docker-compose up --build
