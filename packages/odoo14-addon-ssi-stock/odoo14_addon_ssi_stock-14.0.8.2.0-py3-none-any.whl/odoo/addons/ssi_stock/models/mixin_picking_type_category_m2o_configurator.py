# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class MixinPickingTypeCategoryM2OConfiguratorck(models.AbstractModel):
    _name = "mixin.picking_type_category_m2o_configurator"
    _inherit = [
        "mixin.decorator",
    ]
    _description = "picking_type_category Many2one Configurator Mixin"

    _picking_type_category_m2o_configurator_insert_form_element_ok = False
    _picking_type_category_m2o_configurator_form_xpath = False

    picking_type_category_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Picking Type Category Selection Method",
        required=True,
    )
    picking_type_category_ids = fields.Many2many(
        comodel_name="picking_type_category",
        string="Picking Type Categories",
        relation="rel_m2o_configurator_2_picking_type_category",
    )
    picking_type_category_domain = fields.Text(
        default="[]", string="Picking Type Category Domain"
    )
    picking_type_category_python_code = fields.Text(
        default="result = []", string="Picking Type Category Python Code"
    )

    @ssi_decorator.insert_on_form_view()
    def _picking_type_category_m2o_configurator_insert_form_element(self, view_arch):
        # TODO
        template_xml = "ssi_stock."
        template_xml += "picking_type_category_m2o_configurator_template"
        if self._picking_type_category_m2o_configurator_insert_form_element_ok:
            view_arch = self._add_view_element(
                view_arch=view_arch,
                qweb_template_xml_id=template_xml,
                xpath=self._picking_type_category_m2o_configurator_form_xpath,
                position="inside",
            )
        return view_arch
