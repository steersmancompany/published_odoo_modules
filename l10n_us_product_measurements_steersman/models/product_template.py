# -*- coding: utf-8 -*-

# Standard Odoo imports
from odoo import api, fields, models

import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Modify existing weight and volume fields in default UoM
    weight = fields.Float(string='Weight (Default UoM)', digits=dp.get_precision('Stock Weight'),
                          compute='_compute_weight', store=True, help="Weight in Kilograms.")
    volume = fields.Float(string='Volume (Default UoM)', digits=dp.get_precision('Stock Volume'),
                          compute='_compute_volume', store=True, help="Volume in Cubic Meters.")
    # Add fields for dimensions in default UoM
    length = fields.Float(string='Length (Default UoM)', digits=dp.get_precision('Stock Dimensions'),
                          compute='_compute_length', store=True, help="Length in Centimeters.")
    width = fields.Float(string='Width (Default UoM)', digits=dp.get_precision('Stock Dimensions'),
                         compute='_compute_width', store=True, help="Width in Centimeters.")
    height = fields.Float(string='Height (Default UoM)', digits=dp.get_precision('Stock Dimensions'),
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
    display_weight = fields.Float(string='Weight', digits=dp.get_precision('Stock Weight'),
                                  compute='_compute_display_weight', inverse='_set_display_weight', store=True)
    display_weight_uom_id = fields.Many2one(string='Weight UoM', comodel_name='product.uom',
                                            compute='_compute_display_weight_uom_id', inverse='_set_display_weight_uom_id', store=True,
                                            domain=_get_weight_uom_domain, default=_default_display_weight_uom)
    display_volume = fields.Float(string='Volume', digits=dp.get_precision('Stock Volume'),
                                  compute='_compute_display_volume', inverse='_set_display_volume', store=True)
    display_volume_uom_id = fields.Many2one(string='Volume UoM', comodel_name='product.uom',
                                            compute='_compute_display_volume_uom_id', inverse='_set_display_volume_uom_id', store=True,
                                            domain=_get_volume_uom_domain, default=_default_display_volume_uom)
    display_length = fields.Float(string='Length', digits=dp.get_precision('Stock Dimensions'),
                                  compute='_compute_display_length', inverse='_set_display_length', store=True)
    display_width = fields.Float(string='Width', digits=dp.get_precision('Stock Dimensions'),
                                 compute='_compute_display_width', inverse='_set_display_width', store=True)
    display_height = fields.Float(string='Height', digits=dp.get_precision('Stock Dimensions'),
                                  compute='_compute_display_height', inverse='_set_display_height', store=True)
    display_dimensions_uom_id = fields.Many2one(string='Dimensions UoM', comodel_name='product.uom',
                                                compute='_compute_display_dimensions_uom_id', inverse='_set_display_dimensions_uom_id', store=True,
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
        for t in self.search([]):
            t.write({
                'display_weight': weight_uom._compute_quantity(t.weight, display_weight_uom),
                'display_weight_uom_id': display_weight_uom.id
            })
            t.write({
                'display_volume': volume_uom._compute_quantity(t.volume, display_volume_uom),
                'display_volume_uom_id': display_volume_uom.id
            })

    @api.model
    def create(self, vals):
        """ Trigger an update of values for the first variant
            Default display UoM fields to Odoo default UoM if not entered
        """

        template = super(ProductTemplate, self).create(vals)

        # This is needed to set given values to first variant after creation
        related_vals = {}
        if vals.get('display_weight'):
            related_vals['display_weight'] = vals['display_weight']
        if vals.get('display_weight_uom_id'):
            related_vals['display_weight_uom_id'] = vals['display_weight_uom_id'] or self._default_weight_uom().id
        if vals.get('display_volume'):
            related_vals['display_volume'] = vals['display_volume']
        if vals.get('display_volume_uom_id'):
            related_vals['display_volume_uom_id'] = vals['display_volume_uom_id'] or self._default_volume_uom().id
        if vals.get('display_length'):
            related_vals['display_length'] = vals['display_length']
        if vals.get('display_width'):
            related_vals['display_width'] = vals['display_width']
        if vals.get('display_height'):
            related_vals['display_height'] = vals['display_height']
        if vals.get('display_dimensions_uom_id'):
            related_vals['display_dimensions_uom_id'] = vals['display_dimensions_uom_id'] or self._default_dimensions_uom().id
        template.write(related_vals)

        return template

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

        return super(ProductTemplate, self).write(vals)

    @api.depends('display_weight', 'display_weight_uom_id')
    def _compute_weight(self):
        weight_uom = self._default_weight_uom()
        for t in self:
            display_weight_uom = t.display_weight_uom_id or weight_uom
            t.weight = display_weight_uom._compute_quantity(t.display_weight, weight_uom)

    @api.depends('display_volume', 'display_volume_uom_id')
    def _compute_volume(self):
        volume_uom = self._default_volume_uom()
        for t in self:
            display_volume_uom = t.display_volume_uom_id or volume_uom
            if display_volume_uom:
                t.volume = display_volume_uom._compute_quantity(t.display_volume, volume_uom)

    @api.depends('display_length', 'display_dimensions_uom_id')
    def _compute_length(self):
        dimensions_uom = self._default_dimensions_uom()
        for t in self:
            display_dimensions_uom = t.display_dimensions_uom_id or dimensions_uom
            t.length = display_dimensions_uom._compute_quantity(t.display_length, dimensions_uom)

    @api.depends('display_width', 'display_dimensions_uom_id')
    def _compute_width(self):
        dimensions_uom = self._default_dimensions_uom()
        for t in self:
            display_dimensions_uom = t.display_dimensions_uom_id or dimensions_uom
            t.width = display_dimensions_uom._compute_quantity(t.display_width, dimensions_uom)

    @api.depends('display_height', 'display_dimensions_uom_id')
    def _compute_height(self):
        dimensions_uom = self._default_dimensions_uom()
        for t in self:
            display_dimensions_uom = t.display_dimensions_uom_id or dimensions_uom
            t.height = display_dimensions_uom._compute_quantity(t.display_height, dimensions_uom)

    @api.depends('product_variant_ids', 'product_variant_ids.display_weight')
    def _compute_display_weight(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_weight = t.product_variant_ids.display_weight
            else:
                t.display_weight = 0.0

    @api.one
    def _set_display_weight(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_weight = self.display_weight

    @api.depends('product_variant_ids', 'product_variant_ids.display_weight_uom_id')
    def _compute_display_weight_uom_id(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_weight_uom_id = t.product_variant_ids.display_weight_uom_id
            else:
                t.display_weight_uom_id = None

    @api.one
    def _set_display_weight_uom_id(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_weight_uom_id = self.display_weight_uom_id

    @api.depends('product_variant_ids', 'product_variant_ids.display_volume')
    def _compute_display_volume(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_volume = t.product_variant_ids.display_volume
            else:
                t.display_volume = 0.0

    @api.one
    def _set_display_volume(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_volume = self.display_volume

    @api.depends('product_variant_ids', 'product_variant_ids.display_volume_uom_id')
    def _compute_display_volume_uom_id(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_volume_uom_id = t.product_variant_ids.display_volume_uom_id
            else:
                t.display_volume_uom_id = None

    @api.one
    def _set_display_volume_uom_id(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_volume_uom_id = self.display_volume_uom_id

    @api.depends('product_variant_ids', 'product_variant_ids.display_length')
    def _compute_display_length(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_length = t.product_variant_ids.display_length
            else:
                t.display_length = 0.0

    @api.one
    def _set_display_length(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_length = self.display_length

    @api.depends('product_variant_ids', 'product_variant_ids.display_width')
    def _compute_display_width(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_width = t.product_variant_ids.display_width
            else:
                t.display_width = 0.0

    @api.one
    def _set_display_width(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_width = self.display_width

    @api.depends('product_variant_ids', 'product_variant_ids.display_height')
    def _compute_display_height(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_height = t.product_variant_ids.display_height
            else:
                t.display_height = 0.0

    @api.one
    def _set_display_height(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_height = self.display_height

    @api.depends('product_variant_ids', 'product_variant_ids.display_dimensions_uom_id')
    def _compute_display_dimensions_uom_id(self):
        for t in self:
            if 1 == len(t.product_variant_ids):
                t.display_dimensions_uom_id = t.product_variant_ids.display_dimensions_uom_id
            else:
                t.display_dimensions_uom_id = None

    @api.one
    def _set_display_dimensions_uom_id(self):
        if 1 == len(self.product_variant_ids):
            self.product_variant_ids.display_dimensions_uom_id = self.display_dimensions_uom_id
