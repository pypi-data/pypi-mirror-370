# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassCreateLocation(models.TransientModel):
    _name = "mass_create_location"
    _description = "Mass Create Location"

    @api.model
    def _default_warehouse_ids(self):
        result = []
        if self.env.context.get("active_model", False) == "stock.warehouse":
            result = self.env.context.get("active_ids", [])
        return result

    @api.model
    def _default_location_type_ids(self):
        result = []
        if self.env.context.get("active_model", False) == "location_type":
            result = self.env.context.get("active_ids", [])
        return result

    warehouse_ids = fields.Many2many(
        string="Warehouses",
        comodel_name="stock.warehouse",
        relation="rel_mass_create_location_2_warehouse",
        column1="wizard_id",
        column2="warehouse_id",
        default=lambda self: self._default_warehouse_ids(),
        required=False,
    )
    location_type_ids = fields.Many2many(
        string="Location Types",
        comodel_name="location_type",
        relation="rel_mass_create_location_2_location_type",
        column1="wizard_id",
        column2="type_id",
        default=lambda self: self._default_location_type_ids(),
        required=True,
    )

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        Location = self.env["stock.location"]
        for warehouse in self.warehouse_ids:
            for loc_type in self.location_type_ids:
                criteria = [
                    ("type_id", "=", loc_type.id),
                ]
                if loc_type.is_warehouse_location:
                    criteria += [("warehouse_id", "=", warehouse.id)]
                loc_count = Location.search_count(criteria)
                if loc_count == 0:
                    Location.create(loc_type._prepare_location_data(warehouse))
