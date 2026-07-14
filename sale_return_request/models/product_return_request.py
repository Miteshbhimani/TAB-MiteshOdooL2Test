from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class ProductReturnRequest(models.Model):
    _name = 'product.return.request'
    _description = 'Product Return Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', default='New', copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, tracking=True, domain="[('partner_id', '=', partner_id), ('state', '=', 'sale')]")
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Return Quantity', required=True, default=1.0)
    reason = fields.Selection(
        [
            ('damaged', 'Damaged'),
            ('wrong_item', 'Wrong Item'),
            ('no_longer_needed', 'No Longer Needed'),
            ('other', 'Other'),
        ], string='Reason', required=True, default='damaged')
    reason_note = fields.Text(string='Reason Note')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ], string='Status', default='draft', tracking=True, copy=False)

    available_product_ids = fields.Many2many('product.product', compute='_compute_available_product_ids')

    @api.depends('sale_order_id')
    def _compute_available_product_ids(self):
        for rec in self:
            if rec.sale_order_id:
                rec.available_product_ids = rec.sale_order_id.order_line.mapped('product_id')
            else:
                rec.available_product_ids = False

    # Optional: reset product when SO changes
    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        self.product_id = False

    # @api.onchange('sale_order_id')
    # def _onchange_sale_order_id(self):
    #     self.product_id = False
    #     if self.sale_order_id:
    #         order_products = self.sale_order_id.order_line.mapped('product_id')
    #         return {'domain': {'product_id': [('id', 'in', order_products.ids)]}}
    #     return {'domain': {'product_id': []}}

    @api.constrains('reason', 'reason_note')
    def _check_reason_note(self):
        for request in self:
            if request.reason == 'other' and not request.reason_note:
                raise ValidationError('Please enter a reason note when reason is set to Other.')

    @api.constrains('sale_order_id', 'product_id')
    def _check_product_on_order(self):
        for request in self:
            if request.sale_order_id and request.product_id:
                order_products = request.sale_order_id.order_line.mapped('product_id')
                if request.product_id not in order_products:
                    raise ValidationError('The selected product is not part of the selected sale order.')

    @api.constrains('quantity', 'sale_order_id', 'product_id')
    def _check_quantity(self):
        for request in self:
            if not request.sale_order_id or not request.product_id:
                continue
            order_lines = request.sale_order_id.order_line.filtered(lambda line: line.product_id == request.product_id)
            delivered_qty = sum(order_lines.mapped('qty_delivered'))
            if request.quantity > delivered_qty:
                raise ValidationError('Return quantity %s cannot exceed the delivered quantity '
                    '%s of %s on this order.' % (request.quantity, delivered_qty, request.product_id.display_name))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('product.return.request') or 'New'
        return super().create(vals_list)

    def unlink(self):
        for request in self:
            if request.state != 'draft':
                raise UserError('You cannot delete a return request that is no longer in draft.')
        return super().unlink()

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        if not self.env.user.has_group('sale_return_request.group_return_manager'):
            raise UserError('Only users in the Return Manager group can approve return requests.')
        for request in self:
            request.state = 'approved'
            request.sale_order_id.message_post(
                body='Return %s approved for %s x %s' % (request.name, request.quantity, request.product_id.display_name
                ))

    def action_reject(self):
        if not self.env.user.has_group('sale_return_request.group_return_manager'):
            raise UserError('Only users in the Return Manager group can reject return requests.')
        self.write({'state': 'rejected'})
