# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = [
        "stock.picking",
        "mixin.print_document",
        "mixin.policy",
        "mixin.multiple_approval",
    ]
    _automatically_insert_print_button = True

    _approval_from_state = "confirmed"
    _approval_to_state = "done"
    _approval_state = "assigned"
    _after_approved_method = "button_validate"
    _automatically_insert_multiple_approval_page = True

    picking_type_category_id = fields.Many2one(
        string="Picking Type Category",
        related="picking_type_id.category_id",
        store=True,
    )
    partner_tag_ids = fields.Many2many(
        string="Partner Tags",
        related="partner_id.category_id",
        store=False,
    )
    show_price_unit = fields.Boolean(
        string="Show Price Unit",
        related="picking_type_id.show_price_unit",
        store=False,
    )
    show_procure_method = fields.Boolean(
        string="Show Procure Method",
        related="picking_type_id.show_procure_method",
        store=False,
    )
    allowed_source_location_ids = fields.Many2many(
        string="Allowed Source Locations",
        comodel_name="stock.location",
        compute="_compute_allowed_source_location_ids",
        related=False,
        store=False,
    )
    allowed_destination_location_ids = fields.Many2many(
        string="Allowed Destination Locations",
        comodel_name="stock.location",
        compute="_compute_allowed_destination_location_ids",
        related=False,
        store=False,
    )
    allowed_product_category_ids = fields.Many2many(
        string="Allowed Product Categories",
        comodel_name="product.category",
        related="picking_type_id.allowed_product_category_ids",
        store=False,
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed Products",
        comodel_name="product.product",
        related="picking_type_id.allowed_product_ids",
        store=False,
    )
    mark_as_todo_ok = fields.Boolean(
        string="Can Mark As To Do",
        compute="_compute_policy",
        compute_sudo=True,
    )
    check_availability_ok = fields.Boolean(
        string="Can Check Availability",
        compute="_compute_policy",
        compute_sudo=True,
    )
    unreserved_ok = fields.Boolean(
        string="Can Unreserved",
        compute="_compute_policy",
        compute_sudo=True,
    )
    return_ok = fields.Boolean(
        string="Can Return",
        compute="_compute_policy",
        compute_sudo=True,
    )
    validate_ok = fields.Boolean(
        string="Can Validate",
        compute="_compute_policy",
        compute_sudo=True,
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
        compute_sudo=True,
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
        compute_sudo=True,
    )
    change_actual_movement_date_ok = fields.Boolean(
        string="Can Change Actual Movement Date",
        compute="_compute_policy",
        compute_sudo=True,
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Approve policy

* If active user can see and execute 'Approve' button""",
    )
    reject_ok = fields.Boolean(
        string="Can Reject",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Reject policy

* If active user can see and execute 'Reject' button""",
    )
    restart_approval_ok = fields.Boolean(
        string="Can Restart Approval",
        compute="_compute_policy",
        compute_sudo=True,
        help="""Restart approval policy

* If active user can see and execute 'Restart Approval' button""",
    )

    def _compute_policy(self):
        _super = super(StockPicking, self)
        _super._compute_policy()

    @api.depends(
        "picking_type_id",
    )
    def _compute_allowed_source_location_ids(self):
        Location = self.env["stock.location"]
        for record in self:
            result = []
            if record.picking_type_id:
                ptype = record.picking_type_id
                result += ptype.allowed_source_location_ids.ids

                for loc_type in ptype.allowed_source_location_type_ids:
                    criteria = False
                    if loc_type.is_warehouse_location and ptype.warehouse_id:
                        criteria = [
                            ("type_id", "=", loc_type.id),
                            ("warehouse_id", "=", ptype.warehouse_id.id),
                        ]
                    elif not loc_type.is_warehouse_location:
                        criteria = [
                            ("type_id", "=", loc_type.id),
                        ]
                    if criteria:
                        result += Location.search(criteria).ids
            record.allowed_source_location_ids = result

    @api.depends(
        "picking_type_id",
    )
    def _compute_allowed_destination_location_ids(self):
        Location = self.env["stock.location"]
        for record in self:
            result = []
            if record.picking_type_id:
                ptype = record.picking_type_id
                result += ptype.allowed_destination_location_ids.ids

                for loc_type in ptype.allowed_destination_location_type_ids:
                    criteria = False
                    if loc_type.is_warehouse_location and ptype.warehouse_id:
                        criteria = [
                            ("type_id", "=", loc_type.id),
                            ("warehouse_id", "=", ptype.warehouse_id.id),
                        ]
                    elif not loc_type.is_warehouse_location:
                        criteria = [
                            ("type_id", "=", loc_type.id),
                        ]
                    if criteria:
                        result += Location.search(criteria).ids
            record.allowed_destination_location_ids = result

    @api.model
    def _get_policy_field(self):
        res = super(StockPicking, self)._get_policy_field()
        policy_field = [
            "mark_as_todo_ok",
            "check_availability_ok",
            "unreserved_ok",
            "cancel_ok",
            "restart_ok",
            "validate_ok",
            "return_ok",
            "change_actual_movement_date_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
        ]
        res += policy_field
        return res

    def _assign_auto_lot_number(self):
        for record in self:
            if record.picking_type_id.use_create_lots:
                for line in record.mapped("move_line_ids").filtered(
                    lambda x: (
                        not x.lot_id
                        and not x.lot_name
                        and x.product_id.tracking != "none"
                        and x.product_id.categ_id.sequence_id
                        and x.qty_done != 0.0
                    )
                ):
                    line._assign_auto_lot_number()

    def _action_done(self):
        self._assign_auto_lot_number()
        return super()._action_done()

    def button_validate(self):
        self._assign_auto_lot_number()
        return super().button_validate()

    def action_draft(self):
        self.move_lines.action_draft()
