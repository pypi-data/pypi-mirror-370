# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassCreatePickingType(models.TransientModel):
    _name = "mass_create_picking_type"
    _description = "Mass Picking Type"

    @api.model
    def _default_warehouse_ids(self):
        result = []
        if self.env.context.get("active_model", False) == "stock.warehouse":
            result = self.env.context.get("active_ids", [])
        return result

    @api.model
    def _default_picking_type_category_ids(self):
        result = []
        if self.env.context.get("active_model", False) == "picking_type_category":
            result = self.env.context.get("active_ids", [])
        return result

    warehouse_ids = fields.Many2many(
        string="Warehouses",
        comodel_name="stock.warehouse",
        relation="rel_mass_create_picking_type_2_warehouse",
        column1="wizard_id",
        column2="warehouse_id",
        default=lambda self: self._default_warehouse_ids(),
        required=True,
    )
    picking_type_category_ids = fields.Many2many(
        string="Picking Type Categories",
        comodel_name="picking_type_category",
        relation="rel_mass_create_picking_type_2_picking_type_category",
        column1="wizard_id",
        column2="type_id",
        default=lambda self: self._default_picking_type_category_ids(),
        required=True,
    )

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        PickingType = self.env["stock.picking.type"]
        for warehouse in self.warehouse_ids:
            for type_categ in self.picking_type_category_ids:
                PickingType.create(type_categ._prepare_picking_type_data(warehouse))
