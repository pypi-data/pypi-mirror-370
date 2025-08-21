# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class PickingTypeCategory(models.Model):
    _name = "picking_type_category"
    _inherit = ["mixin.master_data"]
    _description = "Picking Type Category"

    direction = fields.Selection(
        string="Direction",
        selection=[
            ("incoming", "Receipt"),
            ("outgoing", "Delivery"),
            ("internal", "Internal"),
        ],
        required=True,
        default="internal",
    )
    show_operations = fields.Boolean(
        string="Show Detailed Operations",
    )
    show_reserved = fields.Boolean(
        string="Pre-fill Detailed Operations",
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
    use_create_lots = fields.Boolean(
        string="Create New Lot/Serial Number",
    )
    use_existing_lots = fields.Boolean(
        string="Use Existing Lot/Serial Number",
    )

    default_source_location_type_id = fields.Many2one(
        string="Default Source Location Type",
        comodel_name="location_type",
    )
    allowed_source_location_type_ids = fields.Many2many(
        string="Allowed Source Location Types",
        comodel_name="location_type",
        relation="rel_picking_type_category_2_source_location_type",
        column1="category_id",
        column2="type_id",
    )
    default_destination_location_type_id = fields.Many2one(
        string="Default Destination Location Type",
        comodel_name="location_type",
    )
    allowed_destination_location_type_ids = fields.Many2many(
        string="Allowed Destination Location Types",
        comodel_name="location_type",
        relation="rel_picking_type_category_2_destination_location_type",
        column1="category_id",
        column2="type_id",
    )
    allowed_product_category_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        relation="rel_picking_type_category_2_product_category",
        column1="category_id",
        column2="product_category_id",
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        relation="rel_picking_type_category_2_product",
        column1="category_id",
        column2="product_id",
    )
    menu_id = fields.Many2one(
        string="Menu",
        comodel_name="ir.ui.menu",
        readonly=True,
    )
    window_action_id = fields.Many2one(
        string="Window Action",
        comodel_name="ir.actions.act_window",
        readonly=True,
    )

    def action_create_menu(self):
        for record in self.sudo():
            record._create_menu()

    def action_delete_menu(self):
        for record in self.sudo():
            record._delete_menu()

    def action_reload_configuration(self):
        for record in self.sudo():
            record._reload_configuration()

    def _reload_configuration(self):
        self.ensure_one()
        PickingType = self.env["stock.picking.type"]
        criteria = [("category_id", "=", self.id)]
        for picking_type in PickingType.search(criteria):
            picking_type._reload_configuration()

    def _delete_menu(self):
        self.menu_id.unlink()
        self.window_action_id.unlink()

    def _create_menu(self):
        self.ensure_one()
        Menu = self.env["ir.ui.menu"]
        Waction = self.env["ir.actions.act_window"]

        waction = Waction.create(self._prepare_waction())
        self.write(
            {
                "window_action_id": waction.id,
            }
        )
        menu = Menu.create(self._prepare_menu())
        self.write(
            {
                "menu_id": menu.id,
            }
        )

    def _prepare_waction(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "target": "current",
            "view_mode": "tree,form",
            "domain": [("picking_type_category_id", "=", self.id)],
            "context": {"default_picking_type_category_id": self.id},
        }

    def _prepare_menu(self):
        self.ensure_one()
        action = "ir.actions.act_window,%s" % self.window_action_id.id
        return {
            "name": self.name,
            "parent_id": self.env.ref("stock.menu_stock_warehouse_mgmt").id,
            "action": action,
        }

    def _prepare_picking_type_data(self, warehouse):
        self.ensure_one()
        data_standard = self._prepare_standard_picking_type_data(warehouse)
        return data_standard

    def _prepare_standard_picking_type_data(self, warehouse):
        self.ensure_one()
        source_locations = self._get_allowed_source_location(warehouse)
        destination_locations = self._get_allowed_destination_location(warehouse)
        default_source_location = self._get_default_source_location(warehouse)
        default_destination_location = self._get_default_destination_location(warehouse)
        result = {
            "name": self.name,
            "sequence_code": self.code,
            "code": self.direction,
            "category_id": self.id,
            "warehouse_id": warehouse.id,
            "show_operations": self.show_operations,
            "show_reserved": self.show_reserved,
            "show_price_unit": self.show_price_unit,
            "procure_method": self.procure_method,
            "use_create_lots": self.use_create_lots,
            "use_existing_lots": self.use_existing_lots,
            "allowed_source_location_ids": [(6, 0, source_locations.ids)],
            "allowed_destination_location_ids": [(6, 0, destination_locations.ids)],
            "default_location_src_id": default_source_location
            and default_source_location.id
            or False,
            "default_location_dest_id": default_destination_location
            and default_destination_location.id
            or False,
            "allowed_product_category_ids": [
                (6, 0, self.allowed_product_category_ids.ids)
            ],
            "allowed_product_ids": [(6, 0, self.allowed_product_ids.ids)],
        }
        return result

    def _get_allowed_source_location(self, warehouse):
        self.ensure_one()
        result = self.env["stock.location"]

        for loc_type in self.allowed_source_location_type_ids:
            result += loc_type._get_location(warehouse)
        return result

    def _get_allowed_destination_location(self, warehouse):
        self.ensure_one()
        result = self.env["stock.location"]

        for loc_type in self.allowed_destination_location_type_ids:
            result += loc_type._get_location(warehouse)
        return result

    def _get_default_source_location(self, warehouse):
        self.ensure_one()
        result = False
        if self.default_source_location_type_id:
            locations = self.default_source_location_type_id._get_location(warehouse)
            if len(locations) > 0:
                result = locations[0]
        return result

    def _get_default_destination_location(self, warehouse):
        self.ensure_one()
        result = False
        if self.default_destination_location_type_id:
            locations = self.default_destination_location_type_id._get_location(
                warehouse
            )
            if len(locations) > 0:
                result = locations[0]
        return result
