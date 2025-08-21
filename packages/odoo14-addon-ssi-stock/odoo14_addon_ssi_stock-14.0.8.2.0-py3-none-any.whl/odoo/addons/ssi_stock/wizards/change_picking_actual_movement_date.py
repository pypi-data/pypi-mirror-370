# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ChangePickingActualMovementDate(models.TransientModel):
    _name = "change_picking_actual_movement_date"
    _description = "Change Picking Actual Movement Date"

    @api.model
    def _default_picking_ids(self):
        result = []
        if self.env.context.get("active_model", False) == "stock.picking":
            result = self.env.context.get("active_ids", [])
        return result

    picking_ids = fields.Many2many(
        string="Pickings",
        comodel_name="stock.picking",
        relation="rel_change_picking_actual_move_date_2_picking",
        column1="wizard_id",
        column2="picking_id",
        default=lambda self: self._default_picking_ids(),
        required=False,
    )
    actual_movement_date = fields.Datetime(
        string="Actual Movement date",
        required=True,
    )

    def action_confirm(self):
        for record in self.sudo():
            record._confirm()

    def _confirm(self):
        self.ensure_one()
        self._update_picking_actual_movement_date()
        self._update_stock_move_actual_movement_date()
        self._update_stock_move_line_actual_movement_date()

    def _update_picking_actual_movement_date(self):
        self.ensure_one()
        data = {
            "date_backdating": self.actual_movement_date,
            "date_done": self.actual_movement_date,
        }
        self.picking_ids.write(data)

    def _update_stock_move_actual_movement_date(self):
        self.ensure_one()
        data = {
            "date": self.actual_movement_date,
        }
        self.picking_ids.move_lines.write(data)

    def _update_stock_move_line_actual_movement_date(self):
        self.ensure_one()
        data = {
            "date": self.actual_movement_date,
        }
        self.picking_ids.move_line_ids.write(data)
