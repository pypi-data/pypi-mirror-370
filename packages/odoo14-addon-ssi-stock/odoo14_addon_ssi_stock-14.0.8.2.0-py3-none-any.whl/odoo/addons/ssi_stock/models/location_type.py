# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class LocationType(models.Model):
    _name = "location_type"
    _inherit = ["mixin.master_data"]
    _description = "Picking Type Category"

    usage = fields.Selection(
        string="Usage",
        selection=[
            ("supplier", "Vendor Location"),
            ("view", "View"),
            ("internal", "Internal Location"),
            ("customer", "Customer Location"),
            ("inventory", "Inventory Loss"),
            ("production", "Production"),
            ("transit", "Transit Location"),
        ],
        required=True,
        default="internal",
    )
    parent_location_type_id = fields.Many2one(
        string="Parent Location Type",
        comodel_name="location_type",
    )
    is_warehouse_location = fields.Boolean(
        string="Is Warehouse Location",
    )

    def _prepare_location_data(self, warehouse):
        self.ensure_one()
        location = False
        if self.parent_location_type_id:
            locations = self.parent_location_type_id._get_location(warehouse)
            if len(locations) > 0:
                location = locations[0]

        result = {
            "name": self.name,
            "usage": self.usage,
            "location_id": location and location.id or False,
            "type_id": self.id,
        }
        return result

    def _get_location(self, warehouse=False):
        self.ensure_one()
        Location = self.env["stock.location"]
        criteria = [("type_id", "=", self.id)]
        if self.is_warehouse_location and warehouse:
            criteria += [("warehouse_id", "=", warehouse.id)]
        return Location.search(criteria)
