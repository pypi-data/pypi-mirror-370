# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class APIKeyDescription(models.TransientModel):
    _inherit = "res.users.apikeys.description"

    scope = fields.Selection(
        selection_add=[("fastapi", "Fastapi")],
    )
