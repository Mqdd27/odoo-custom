from odoo import models, fields, api
from odoo.exceptions import UserError


class Movies(models.Model):
    _name = 'movies.movies'
    _description = 'Movies'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    name = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Text(string='Description')
    release_date = fields.Date(string='Release Date', tracking=True)
    watched = fields.Boolean(string='Watched', default=False, tracking=True, compute="_compute_watched", store=True)
    watch_status = fields.Selection([
        ('watching', 'Watching'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('dropped', 'Dropped'),
        ('plan_to_watch', 'Plan to Watch'),
    ], string='Watch Status', default='plan_to_watch', tracking=True)
    date_watched = fields.Date(string='Date Watched', compute="_compute_date_watched", store=True, tracking=True)
    image = fields.Binary(string='Image')
    rating = fields.Selection([
        ('0', '0 Star'),
        ('1', '1 Star'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ], string='Rating', default='0', tracking=True)
    source = fields.Char(string='Source', tracking=True)

    def unlink(self):
        for record in self:
            if record.watched:
                raise UserError("You cannot delete a movie that has been watched.")
        return super(Movies, self).unlink()


    @api.depends('watch_status')
    def _compute_date_watched(self):
        for record in self:
            if record.watch_status == 'completed':
                record.date_watched = fields.Date.today()
                record.watched= True
            else:
                record.date_watched = False
                record.watched= False

    def action_mark_watched(self):
        for record in self:
            record.watched = True

    def action_mark_unwatched(self):
        for record in self:
            record.watched = False
