# -*- coding: utf-8 -*-

# Standard Odoo imports
from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mfg_id = fields.Many2one(string='Manufacturer', comodel_name='res.partner', ondelete='restrict', index=True)
    mfg_product_code = fields.Char(string='MPN', compute='_compute_mfg_product_code',
                                   inverse='_set_mfg_product_code', store=True, index=True)
    map_price = fields.Float(string='MAP', digits=dp.get_precision('Product Price'))

    @api.model
    def create(self, vals):
        """ Trigger an update of values for the first variant
            Default display UoM fields to Odoo default UoM if not entered
        """
        template = super(ProductTemplate, self).create(vals)
        # This is needed to set given values to first variant after creation
        related_vals = {}
        if vals.get('mfg_product_code'):
            related_vals['mfg_product_code'] = vals['mfg_product_code']
        template.write(related_vals)
        return template

    @api.depends('product_variant_ids', 'product_variant_ids.mfg_product_code')
    def _compute_mfg_product_code(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.mfg_product_code = t.product_variant_ids.mfg_product_code
            else:
                t.mfg_product_code = None

    @api.one
    def _set_mfg_product_code(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.mfg_product_code = self.mfg_product_code