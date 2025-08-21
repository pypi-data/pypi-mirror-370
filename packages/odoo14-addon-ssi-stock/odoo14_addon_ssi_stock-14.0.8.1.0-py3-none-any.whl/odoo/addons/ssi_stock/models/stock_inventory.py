from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _selection_filter(self):
        res = super(StockInventory, self)._selection_filter()
        res.append(("moving_product", _("By Moving Products")))
        return res

    def _prepare_inventory_filter(self):
        products = super()._prepare_inventory_filter()
        if self.filter == "moving_product":
            datetime_format = "%Y-%m-%d %H:%M:%S"
            user_tz = self.env.user.tz or "Asia/Jakarta"
            current_datetime = pytz.UTC.localize(datetime.now()).astimezone(
                pytz.timezone(user_tz)
            )
            utc = datetime.now().strftime(datetime_format)
            utc = datetime.strptime(utc, datetime_format)
            tz = current_datetime.strftime(datetime_format)
            tz = datetime.strptime(tz, datetime_format)
            duration = tz - utc
            hours = duration.seconds / 60 / 60
            current_date = current_datetime.date()
            start_date = current_date.strftime("%Y-%m-%d 00:00:00")
            end_date = current_date.strftime("%Y-%m-%d 23:59:59")
            start_date = datetime.strptime(start_date, datetime_format) - relativedelta(
                hours=hours
            )
            end_date = datetime.strptime(end_date, datetime_format) - relativedelta(
                hours=hours
            )
            criteria = [
                ("date", ">=", start_date),
                ("date", "<=", end_date),
                ("state", "=", "done"),
            ]
            move_ids = self.env["stock.move"].search(criteria)
            products = move_ids.mapped("product_id")
        return products

    def _get_inventory_lines_values(self):
        vals = super()._get_inventory_lines_values()
        if self.filter == "moving_product" and not self.product_ids:
            vals = []
        return vals
