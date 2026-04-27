# -*- coding: utf-8 -*-
{
    "name": "Odoo Data Cleaner Pro (Odoo 19)",
    "version": "1.0",
    "license": "OPL-1",
    "price": 59.0,
    "currency": "EUR",
    "category": "Extra Tools",
    "summary": "Clean and reset Odoo database safely with one click.",
    "author": "michaelnabil.com",
    "depends": ["base", "sale_management", "purchase", "stock", "project", "mrp"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/clear_data_wizard_view.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
    "images": ["static/description/banner.png", "static/description/thumbnail.png"],
    "license": "OPL-1",
}
