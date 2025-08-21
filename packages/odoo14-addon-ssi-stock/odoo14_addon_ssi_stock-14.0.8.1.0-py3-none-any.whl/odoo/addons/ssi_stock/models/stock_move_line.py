# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line"]

    def _assign_auto_lot_number(self):
        self.ensure_one()

        if self.product_id.tracking == "none":
            return True

        if self.lot_name or self.lot_id:
            return True

        if not self.product_id.categ_id.sequence_id:
            return True

        sequence = self.product_id.categ_id.sequence_id
        if self.move_id.date_backdating:
            ctx = {"ir_sequence_date": self.move_id.date_backdating}
            number = sequence.with_context(ctx).next_by_id()
        else:
            number = sequence.next_by_id()
        self.write(
            {
                "lot_name": number,
            }
        )

    def _action_cancel_done(self):
        for ml in self.filtered(lambda ml: ml.state == "done"):
            last_move_line_id = (
                self.env["stock.move.line"]
                .sudo()
                .search(
                    [
                        ("state", "=", "done"),
                        ("date", ">", ml.date),
                        ("product_id", "=", ml.product_id.id),
                        ("lot_id", "=", ml.lot_id.id),
                        ("picking_id", "!=", False),
                    ],
                    order="date asc",
                    limit=1,
                )
            )
            if last_move_line_id and not self.env.context.get("bypass_check", False):
                raise ValidationError(
                    _(
                        f"Please cancel transfer {last_move_line_id.picking_id.name} first."
                    )
                )
            quant_obj = self.env["stock.quant"]
            quant_obj._update_available_quantity(
                ml.product_id,
                ml.location_id,
                ml.qty_done,
                lot_id=ml.lot_id,
                package_id=ml.package_id,
                owner_id=ml.owner_id,
            )
            quant_obj._update_available_quantity(
                ml.product_id,
                ml.location_dest_id,
                -ml.qty_done,
                lot_id=ml.lot_id,
                package_id=ml.result_package_id,
                owner_id=ml.owner_id,
            )
