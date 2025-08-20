# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerTitle(models.Model):
    _inherit = "res.partner.title"

    # We need to have this code to make the API work for titles
    # created by hand by the user that don't have any XMLID
    stay_code = fields.Char(
        copy=False, help="Technical code used by the stay API. Do not modify!"
    )

    _sql_constraints = [
        ("stay_code_uniq", "unique(stay_code)", "This stay code already exists.")
    ]
