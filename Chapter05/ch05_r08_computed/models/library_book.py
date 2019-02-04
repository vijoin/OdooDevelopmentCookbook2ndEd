from datetime import timedelta
from odoo import models, fields
from odoo import api
from odoo.fields import Date as fDate


class LibraryBook(models.Model):
    _name = 'library.book'
    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many('res.partner', string='Authors')

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=False,
    )

    @api.depends('date_release')
    def _compute_age(self):
        today = fDate.context_today(self)
        for book in self.filtered('date_release'):
            delta = today - book.date_release
            book.age_days = delta.days

    def _inverse_age(self):
        today = fDate.context_today(self)
        for book in self.filtered('date_release'):
            d = fDate.subtract(today, days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fDate.context_today(self)
        value_date = fDate.subtract(today, days=value)
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<',
            '>=': '<=',
            '<': '>',
            '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]
