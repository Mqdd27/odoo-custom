from odoo import models, fields, api


class SubscriptionCategory(models.Model):
    _name = 'subscription.category'
    _description = 'Subscription Category'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    _name_unique = models.Constraint('UNIQUE(name)', 'Category name must be unique.')


class SubscriptionService(models.Model):
    _name = 'subscription.service'
    _description = 'Subscription Service'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    category_id = fields.Many2one('subscription.category', string='Category')
    website = fields.Char(string='Website')
    logo = fields.Binary(string='Logo')
    active = fields.Boolean(string='Active', default=True)

    _name_unique = models.Constraint('UNIQUE(name)', 'Service name must be unique.')


class Subscription(models.Model):
    _name = 'subscription.subscription'
    _description = 'Subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    name = fields.Char(string='Name', required=True, tracking=True, default=lambda self: f"Subscription {fields.Date.today()}")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, tracking=True, default=lambda self: self.env.company.currency_id)
    subscription_line = fields.One2many('subscription.line', 'subscription_id', string='Subscription Lines')
    total_expenses = fields.Monetary(string='Total Expenses', compute='_compute_totals', store=True, tracking=True)
    total_subscriptions = fields.Integer(string='Total Subscriptions', compute='_compute_totals', store=True, tracking=True)

    @api.depends('subscription_line.price')
    def _compute_totals(self):
        for record in self:
            record.total_subscriptions = len(record.subscription_line)
            record.total_expenses = sum(record.subscription_line.mapped('price'))


class SubscriptionLine(models.Model):
    _name = 'subscription.line'
    _description = 'Subscription Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _rec_name = 'service_id'

    subscription_id = fields.Many2one('subscription.subscription', string='Subscription', required=True, ondelete='cascade')
    service_id = fields.Many2one('subscription.service', string='Service', required=True, tracking=True)
    start_date = fields.Date(string='Start Date', required=True, tracking=True, default=fields.Date.today)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    subscription_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('3monthly', '3 Months'),
        ('6monthly', '6 Months'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ], string='Subscription Type', required=True, tracking=True, default='monthly')
    # Not stored: depends on today's date, so it must be recomputed on every read.
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    ], string='Status', compute='_compute_status')
    price = fields.Monetary(string='Price', required=True, tracking=True)
    currency_id = fields.Many2one(related='subscription_id.currency_id')

    @api.depends('start_date', 'expiry_date', 'subscription_type')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if record.subscription_type == 'lifetime':
                record.status = 'active'
            elif record.start_date and today < record.start_date:
                record.status = 'inactive'
            elif record.expiry_date and today > record.expiry_date:
                record.status = 'expired'
            else:
                record.status = 'active'
