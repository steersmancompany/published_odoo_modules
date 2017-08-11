# -*- coding: utf-8 -*-

# Standard Odoo imports
from odoo import api, fields, models

import odoo.addons.decimal_precision as dp

class Product(models.Model):
    _inherit = "product.product"

    # Modify existing weight and volume fields in default UoM
    weight = fields.Float(string='Weight (Default UoM)', digits=dp.get_precision('Stock Weight'), groups="base.group_no_one",
                          compute='_compute_weight', store=True, help="Weight in Kilograms.")
    volume = fields.Float(string='Volume (Default UoM)', digits=dp.get_precision('Stock Volume'), groups="base.group_no_one",
                          compute='_compute_volume', store=True, help="Volume in Cubic Meters.")
    # Add fields for dimensions in default UoM
    length = fields.Float(string='Length (Default UoM)', digits=dp.get_precision('Stock Dimensions'), groups="base.group_no_one",
                          compute='_compute_length', store=True, help="Length in Centimeters.")
    width = fields.Float(string='Width (Default UoM)', digits=dp.get_precision('Stock Dimensions'), groups="base.group_no_one",
                         compute='_compute_width', store=True, help="Width in Centimeters.")
    height = fields.Float(string='Height (Default UoM)', digits=dp.get_precision('Stock Dimensions'), groups="base.group_no_one",
                          compute='_compute_height', store=True, help="Height in Centimeters.")

    @api.model
    def _get_weight_uom_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]

    @api.model
    def _get_volume_uom_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_vol').id)]

    @api.model
    def _get_dimensions_uom_domain(self):
        return [('category_id', '=', self.env.ref('product.uom_categ_length').id)]

    @api.model
    def _default_display_weight_uom(self):
        return self.env.ref('product.product_uom_lb')

    @api.model
    def _default_display_volume_uom(self):
        return self.env.ref('l10n_us_product_measurements_steersman.product_uom_ft3', raise_if_not_found=False)

    @api.model
    def _default_display_dimensions_uom(self):
        return self.env.ref('product.product_uom_inch')

    # Add display fields for weight, volume and dimensions in user selected UoM
    display_weight = fields.Float(string='Weight', digits=dp.get_precision('Stock Weight'))
    display_weight_uom_id = fields.Many2one(string='Weight UoM', comodel_name='product.uom',
                                            domain=_get_weight_uom_domain, default=_default_display_weight_uom)
    display_volume = fields.Float(string='Volume', digits=dp.get_precision('Stock Volume'))
    display_volume_uom_id = fields.Many2one(string='Volume UoM', comodel_name='product.uom',
                                            domain=_get_volume_uom_domain, default=_default_display_volume_uom)
    display_length = fields.Float(string='Length', digits=dp.get_precision('Stock Dimensions'))
    display_width = fields.Float(string='Width', digits=dp.get_precision('Stock Dimensions'))
    display_height = fields.Float(string='Height', digits=dp.get_precision('Stock Dimensions'))
    display_dimensions_uom_id = fields.Many2one(string='Dimensions UoM', comodel_name='product.uom',
                                            domain=_get_dimensions_uom_domain, default=_default_display_dimensions_uom)

    @api.model
    def _default_weight_uom(self):
        return self.env.ref('product.product_uom_kgm')

    @api.model
    def _default_volume_uom(self):
        return self.env.ref('l10n_us_product_measurements_steersman.product_uom_m3', raise_if_not_found=False)

    @api.model
    def _default_dimensions_uom(self):
        return self.env.ref('product.product_uom_meter')

    @api.model
    def _init_display_measurements(self):
        """ Initialize display fields on module install """
        weight_uom = self._default_weight_uom()
        volume_uom = self._default_volume_uom()
        display_weight_uom = self._default_display_weight_uom()
        display_volume_uom = self._default_display_volume_uom()
        for p in self.search([]):
            p.write({
                'display_weight': weight_uom._compute_quantity(p.weight, display_weight_uom),
                'display_weight_uom_id': display_weight_uom.id,
            })
            p.write({
                'display_volume': volume_uom._compute_quantity(p.volume, display_volume_uom),
                'display_volume_uom_id': display_volume_uom.id
            })

    @api.multi
    def write(self, vals):
        """ Default display UoM fields to Odoo default UoM if not entered """
        def not_entered(uom_id):
            if uom_id in vals and not vals[uom_id]:
                return True
            else:
                return False

        if not_entered('display_weight_uom_id'):
            vals['display_weight_uom_id'] = self._default_weight_uom().id
        if not_entered('display_volume_uom_id'):
            vals['display_volume_uom_id'] = self._default_volume_uom().id
        if not_entered('display_dimensions_uom_id'):
            vals['display_dimensions_uom_id'] = self._default_dimensions_uom().id
        return super(Product, self).write(vals)

    @api.depends('display_weight', 'display_weight_uom_id')
    def _compute_weight(self):
        weight_uom = self._default_weight_uom()
        for p in self:
            display_weight_uom = p.display_weight_uom_id or weight_uom
            p.weight = display_weight_uom._compute_quantity(p.display_weight, weight_uom)

    @api.depends('display_volume', 'display_volume_uom_id')
    def _compute_volume(self):
        volume_uom = self._default_volume_uom()
        for p in self:
            display_volume_uom = p.display_volume_uom_id or volume_uom
            if display_volume_uom:
                p.volume = display_volume_uom._compute_quantity(p.display_volume, volume_uom)

    @api.depends('display_length', 'display_dimensions_uom_id')
    def _compute_length(self):
        dimensions_uom = self._default_dimensions_uom()
        for p in self:
            display_dimensions_uom = p.display_dimensions_uom_id or dimensions_uom
            p.length = display_dimensions_uom._compute_quantity(p.display_length, dimensions_uom)

    @api.depends('display_width', 'display_dimensions_uom_id')
    def _compute_width(self):
        dimensions_uom = self._default_dimensions_uom()
        for p in self:
            display_dimensions_uom = p.display_dimensions_uom_id or dimensions_uom
            p.width = display_dimensions_uom._compute_quantity(p.display_width, dimensions_uom)

    @api.depends('display_height', 'display_dimensions_uom_id')
    def _compute_height(self):
        dimensions_uom = self._default_dimensions_uom()
        for p in self:
            display_dimensions_uom = p.display_dimensions_uom_id or dimensions_uom
            p.height = display_dimensions_uom._compute_quantity(p.display_height, dimensions_uom)
