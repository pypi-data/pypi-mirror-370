# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = ["stock.production.lot"]

    @api.depends(
        "stock_move_line_ids",
        "stock_move_line_ids.move_id.state",
        "tracking",
    )
    def _compute_stock_move_line(self):
        for record in self:
            first_sml = last_sml = False
            if record.tracking == "serial":
                criteria = [
                    ("lot_id", "=", record.id),
                    ("move_id.state", "=", "done"),
                ]
                smls = self.env["stock.move.line"].search(
                    criteria, order="date asc, id asc"
                )
                if len(smls) > 0:
                    first_sml = smls[0]
                    last_sml = smls[-1]
            record.first_stock_move_line_id = first_sml
            record.last_stock_move_line_id = last_sml

    tracking = fields.Selection(related="product_id.tracking", store=True)
    stock_move_line_ids = fields.One2many(
        comodel_name="stock.move.line",
        inverse_name="lot_id",
        string="Stock Move Lines",
        copy=False,
    )
    first_stock_move_line_id = fields.Many2one(
        string="First Stock Move Line",
        comodel_name="stock.move.line",
        compute="_compute_stock_move_line",
        store=True,
    )
    last_stock_move_line_id = fields.Many2one(
        string="Last Stock Move Line",
        comodel_name="stock.move.line",
        compute="_compute_stock_move_line",
        store=True,
    )
    serial_number_in_date = fields.Datetime(
        string="Incoming Date",
        related="first_stock_move_line_id.date",
        store=True,
    )
    serial_number_current_location_id = fields.Many2one(
        string="Current Location",
        related="last_stock_move_line_id.location_dest_id",
        store=True,
    )
    serial_number_acquisition_value = fields.Float(
        string="Acquisition Value",
        related="first_stock_move_line_id.move_id.price_unit",
        store=True,
    )
