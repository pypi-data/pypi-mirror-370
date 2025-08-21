# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class MixinPickingTypeM2OConfiguratorck(models.AbstractModel):
    _name = "mixin.picking_type_m2o_configurator"
    _inherit = [
        "mixin.decorator",
    ]
    _description = "stock.picking.type Many2one Configurator Mixin"

    _picking_type_m2o_configurator_insert_form_element_ok = False
    _picking_type_m2o_configurator_form_xpath = False

    picking_type_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Picking Type Selection Method",
        required=True,
    )
    picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Picking Types",
        relation="rel_m2o_configurator_2_picking_type",
    )
    picking_type_domain = fields.Text(default="[]", string="Picking Type Domain")
    picking_type_python_code = fields.Text(
        default="result = []", string="Picking Type Python Code"
    )

    @ssi_decorator.insert_on_form_view()
    def _picking_type_m2o_configurator_insert_form_element(self, view_arch):
        # TODO
        template_xml = "ssi_stock."
        template_xml += "picking_type_m2o_configurator_template"
        if self._picking_type_m2o_configurator_insert_form_element_ok:
            view_arch = self._add_view_element(
                view_arch=view_arch,
                qweb_template_xml_id=template_xml,
                xpath=self._picking_type_m2o_configurator_form_xpath,
                position="inside",
            )
        return view_arch
