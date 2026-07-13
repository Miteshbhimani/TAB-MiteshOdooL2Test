from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    return_request_count = fields.Integer(
        string='Return Requests',
        compute='_compute_return_request_count',
    )

    def _compute_return_request_count(self):
        for order in self:
            order.return_request_count = self.env['product.return.request'].search_count(
                [('sale_order_id', '=', order.id)])

    def action_view_return_requests(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'sale_return_request.action_product_return_request'
        )
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {
            'default_sale_order_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        return action
