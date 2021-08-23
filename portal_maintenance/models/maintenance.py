# -*- coding: utf-8 -*-

from odoo import models


class Maintenance(models.Model):
    _inherit = 'maintenance.request'

    def _get_formated_duration(self, duration):
        if duration:
            return '{0:02.0f}:{1:02.0f}'.format(*divmod(duration * 60, 60))
        else:
            return '00:00'