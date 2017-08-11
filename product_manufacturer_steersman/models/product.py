# -*- coding: utf-8 -*-

# Standard Odoo imports
from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    mfg_product_code = fields.Char(string='MPN')