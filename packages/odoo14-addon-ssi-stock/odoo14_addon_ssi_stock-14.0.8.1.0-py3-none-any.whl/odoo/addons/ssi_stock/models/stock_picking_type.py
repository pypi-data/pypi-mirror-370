# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockPickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ["stock.picking.type"]

    category_id = fields.Many2one(
        string="Picking Type Category",
        comodel_name="picking_type_category",
    )
    show_price_unit = fields.Boolean(
        string="Show Price Unit",
    )
    show_procure_method = fields.Boolean(
        string="Show Procure Method",
    )
    procure_method = fields.Selection(
        string="Procure Method",
        selection=[
            ("make_to_stock", "Default: Take From Stock"),
            ("make_to_order", "Advanced: Apply Procurement Rules"),
        ],
        required=True,
        default="make_to_stock",
    )
    allowed_source_location_ids = fields.Many2many(
        string="Allowed Source Locations",
        comodel_name="stock.location",
        relation="rel_picking_type_2_source_location",
        column1="picking_type_id",
        column2="location_id",
    )
    allowed_destination_location_ids = fields.Many2many(
        string="Allowed Destination Locations",
        comodel_name="stock.location",
        relation="rel_picking_type_2_destination_location",
        column1="picking_type_id",
        column2="location_id",
    )
    allowed_source_location_type_ids = fields.Many2many(
        string="Allowed Source Location Types",
        comodel_name="location_type",
        relation="rel_picking_type_2_source_location_type",
        column1="picking_type_id",
        column2="location_type_id",
    )
    allowed_destination_location_type_ids = fields.Many2many(
        string="Allowed Destination Location Types",
        comodel_name="location_type",
        relation="rel_picking_type_2_destination_location_type",
        column1="picking_type_id",
        column2="location_type_id",
    )
    allowed_product_category_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        relation="rel_picking_type_2_product_category",
        column1="category_id",
        column2="product_category_id",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        relation="rel_picking_type_2_product",
        column1="category_id",
        column2="product_id",
    )

    def action_reload_configuration(self):
        for record in self.sudo():
            record._reload_configuration()

    def _reload_configuration(self):
        self.ensure_one()
        data = self.category_id._prepare_standard_picking_type_data(self.warehouse_id)
        self.write(data)
