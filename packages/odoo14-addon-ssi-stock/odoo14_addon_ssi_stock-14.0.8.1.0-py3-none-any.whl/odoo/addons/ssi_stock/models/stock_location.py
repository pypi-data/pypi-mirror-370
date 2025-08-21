# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockLocation(models.Model):
    _name = "stock.location"
    _inherit = ["stock.location"]

    type_id = fields.Many2one(
        string="Type",
        comodel_name="location_type",
    )
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        compute="_compute_warehouse_id",
        store=True,
    )

    @api.depends(
        "location_id",
        "location_id.warehouse_id",
    )
    def _compute_warehouse_id(self):
        Warehouse = self.env["stock.warehouse"]
        for record in self:
            result = False
            criteria = [("view_location_id", "parent_of", record._origin.id)]
            warehouses = Warehouse.search(criteria)
            if len(warehouses) > 0:
                result = warehouses[0]
            record.warehouse_id = result
