from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class InvoiceAPI(http.Controller):
    def _get_user_from_key(self):
        headers = request.httprequest.headers
        token = headers.get('X-API-KEY') or headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(' ',1)[1].strip()
        if not token:
            return None
        apikey = request.env['api.key'].sudo().search([('key','=',token),('active','=',True)], limit=1)
        if apikey:
            return apikey.user_id
        return None

    @http.route('/api/v1/invoices/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_invoices(self, **post):
        user = self._get_user_from_key()
        if not user:
            return {'error': 'Authentication failed'}
        data = post.get('data') or post
        invoices = data if isinstance(data, list) else [data]
        results = []
        for inv in invoices:
            try:
                vals = {
                    'move_type': inv.get('move_type', 'out_invoice'),
                    'partner_id': inv.get('partner_id'),
                    'invoice_date': inv.get('invoice_date'),
                }
                lines = inv.get('lines', [])
                aml = []
                for l in lines:
                    line_vals = (0, 0, {
                        'name': l.get('name') or '',
                        'product_id': l.get('product_id'),
                        'quantity': l.get('quantity', 1),
                        'price_unit': l.get('price_unit', 0.0),
                    })
                    aml.append(line_vals)
                if aml:
                    vals['invoice_line_ids'] = aml
                move = request.env['account.move'].sudo(user.id).create(vals)
                results.append({'id': move.id, 'name': move.name})
            except Exception as e:
                _logger.exception('Error creating invoice')
                results.append({'error': str(e)})
        return {'results': results}

    @http.route('/api/v1/invoices/update', type='json', auth='none', methods=['PUT','POST'], csrf=False)
    def update_invoices(self, **post):
        user = self._get_user_from_key()
        if not user:
            return {'error': 'Authentication failed'}
        data = post.get('data') or post
        invoices = data if isinstance(data, list) else [data]
        results = []
        for inv in invoices:
            try:
                move = request.env['account.move'].sudo(user.id).browse(inv.get('id'))
                if not move.exists():
                    raise ValueError('Invoice not found')
                # minimal update: partner_id, invoice_date, state
                vals = {}
                if inv.get('partner_id'):
                    vals['partner_id'] = inv.get('partner_id')
                if inv.get('invoice_date'):
                    vals['invoice_date'] = inv.get('invoice_date')
                if vals:
                    move.write(vals)
                results.append({'id': move.id})
            except Exception as e:
                _logger.exception('Error updating invoice')
                results.append({'error': str(e)})
        return {'results': results}

    @http.route('/api/v1/invoices/register_payment', type='json', auth='none', methods=['POST'], csrf=False)
    def register_payments(self, **post):
        user = self._get_user_from_key()
        if not user:
            return {'error': 'Authentication failed'}
        data = post.get('data') or post
        payments = data if isinstance(data, list) else [data]
        results = []
        for p in payments:
            try:
                move = request.env['account.move'].sudo(user.id).browse(p.get('invoice_id'))
                if not move.exists():
                    raise ValueError('Invoice not found')
                payment_vals = {
                    'payment_type': 'inbound' if move.move_type == 'out_invoice' else 'outbound',
                    'partner_id': move.partner_id.id,
                    'amount': p.get('amount') or float(move.amount_residual),
                    'journal_id': p.get('journal_id'),
                    'payment_date': p.get('payment_date'),
                    'payment_method_id': p.get('payment_method_id'),
                }
                payment = request.env['account.payment'].sudo(user.id).create(payment_vals)
                try:
                    payment.action_post()
                except Exception:
                    # Some setups need action_post or different reconciliation flow; ignore if fails
                    _logger.info("Payment post failed or not required")
                results.append({'payment_id': payment.id})
            except Exception as e:
                _logger.exception('Error registering payment')
                results.append({'error': str(e)})
        return {'results': results}

    @http.route('/api/v1/invoices/list', type='json', auth='none', methods=['GET','POST'], csrf=False)
    def list_invoices(self, **kw):
        user = self._get_user_from_key()
        if not user:
            return {'error': 'Authentication failed'}
        domain = []
        if kw.get('partner_id'):
            domain.append(('partner_id','=',int(kw['partner_id'])))
        invs = request.env['account.move'].sudo(user.id).search(domain, limit=500)
        out = []
        for m in invs:
            payments = []
            # compatibility: try to get reconciled payment ids method, else payment_ids
            if hasattr(m, '_get_reconciled_payment_ids'):
                payment_records = m._get_reconciled_payment_ids()
            else:
                payment_records = getattr(m, 'payment_ids', [])
            for p in payment_records:
                payments.append({'id': p.id, 'amount': float(getattr(p,'amount',0)), 'journal': getattr(getattr(p,'journal_id',False),'name',False)})
            out.append({
                'id': m.id,
                'name': m.name,
                'state': m.state,
                'amount_total': float(m.amount_total),
                'payments': payments,
            })
        return {'invoices': out}
