# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockWarehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse"]

    manager_id = fields.Many2one(
        string="Manager",
        comodel_name="res.users",
    )
    supervisor_ids = fields.Many2many(
        string="Supervisors",
        comodel_name="res.users",
        relation="rel_stock_warehouse_supervisor",
        column1="warehouse_id",
        column2="user_id",
    )
    user_ids = fields.Many2many(
        string="Users",
        comodel_name="res.users",
        relation="rel_stock_warehouse_user",
        column1="warehouse_id",
        column2="user_id",
    )
