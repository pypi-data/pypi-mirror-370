# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category"]

    sequence_id = fields.Many2one(
        string="Sequence",
        comodel_name="ir.sequence",
    )
