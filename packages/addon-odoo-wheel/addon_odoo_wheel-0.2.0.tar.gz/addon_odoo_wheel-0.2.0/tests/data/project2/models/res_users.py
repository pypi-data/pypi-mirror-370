from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    awesome_user = fields.Boolean(string="Awesome User")

    @api.model
    def create(self, vals_list):
        for val in vals_list:
            val["awesome_user"] = val.get("login") == "awesome"
        return super().create(vals_list)
