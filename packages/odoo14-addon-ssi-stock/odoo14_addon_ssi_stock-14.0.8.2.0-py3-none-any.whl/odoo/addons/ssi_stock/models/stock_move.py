# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move"]

    forced_lot_id = fields.Many2one("stock.production.lot")

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        vals["forced_lot_id"] = self.forced_lot_id.id
        return vals

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        self.ensure_one()
        if not lot_id and self.forced_lot_id:
            lot_id = self.forced_lot_id
        return super()._get_available_quantity(
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        self.ensure_one()
        if self.forced_lot_id:
            lot_id = self.forced_lot_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _split(self, qty, restrict_partner_id=False):
        vals_list = super()._split(qty, restrict_partner_id=restrict_partner_id)
        if vals_list and self.forced_lot_id:
            vals_list[0]["forced_lot_id"] = self.forced_lot_id.id
        return vals_list

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.forced_lot_id:
            if (
                "lot_id" in vals
                and vals["lot_id"] is not False
                and vals["lot_id"] != self.forced_lot_id.id
            ):
                raise UserError(
                    _(
                        "Inconsistencies between reserved quant and lot restriction on "
                        "stock move"
                    )
                )
            vals["lot_id"] = self.forced_lot_id.id
        return vals

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super()._prepare_merge_moves_distinct_fields()
        return res + ["forced_lot_id"]

    @api.onchange(
        "picking_type_id",
    )
    def onchange_procure_method(self):
        if self.picking_type_id:
            self.procure_method = self.picking_type_id.procure_method

    def _action_cancel(self):
        for rec in self.filtered(lambda m: m.state == "done"):
            rec.move_line_ids._action_cancel_done()
            rec.write({"state": "cancel"})
        res = super(StockMove, self)._action_cancel()
        return res

    def action_draft(self):
        for rec in self.filtered(lambda m: m.state == "cancel"):
            rec.write({"state": "draft"})
