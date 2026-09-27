from odoo import models, fields, api
from odoo.exceptions import UserError


class Movies(models.Model):
    _name = 'movies.movies'
    _description = 'Movies'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    release_date = fields.Date(string='Release Date')
    watched = fields.Boolean(string='Watched', default=False)
    date_watched = fields.Date(string='Date Watched', compute="_compute_date_watched", store=True)
    image = fields.Binary(string='Image')
    rating = fields.Selection([
        ('0', '0 Star'),
        ('1', '1 Star'),
        ('2', '2 Star'),
        ('3', '3 Star'),
        ('4', '4 Star'),
        ('5', '5 Star'),
    ], string='Rating', default='0')


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
