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
    watched = fields.Boolean(string='Watched', default=False, tracking=True)
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

    def unlink(self):
        for record in self:
            if record.watched:
                raise UserError("You cannot delete a movie that has been watched.")
        return super(Movies, self).unlink()

    @api.depends('watched')
    def _compute_date_watched(self):
        for record in self:
            if record.watched:
                record.date_watched = fields.Date.today()
            else:
                record.date_watched = False

    def action_mark_watched(self):
        for record in self:
            record.watched = True

    def action_mark_unwatched(self):
        for record in self:
            record.watched = False
