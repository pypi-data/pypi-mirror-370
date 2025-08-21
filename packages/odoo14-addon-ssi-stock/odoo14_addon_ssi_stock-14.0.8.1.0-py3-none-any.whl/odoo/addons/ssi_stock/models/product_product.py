# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_domain_locations(self):
        res = super()._get_domain_locations()
        lot_id = self.env.context.get("lot_id")
        if not lot_id:
            return res

        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = res
        lot_domain = [("forced_lot_id", "=", lot_id)]
        domain_move_in_loc += lot_domain
        domain_move_out_loc += lot_domain
        return domain_quant_loc, domain_move_in_loc, domain_move_out_loc
