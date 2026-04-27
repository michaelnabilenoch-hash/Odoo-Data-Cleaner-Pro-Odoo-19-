# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ClearDataWizard(models.TransientModel):
    _name = "clear.data.wizard"
    _description = "Mass Data Clear Wizard"

    all_data = fields.Boolean("All Data")
    sale = fields.Boolean("Sales & Transfers")
    purchase = fields.Boolean("Purchases & Transfers")
    inventory = fields.Boolean("Stock Operations")
    projects = fields.Boolean("Projects & Tasks")
    contacts = fields.Boolean("Customers & Vendors")

    @api.onchange("all_data")
    def _onchange_all_data(self):
        if self.all_data:
            self.sale = True
            self.purchase = True
            self.inventory = True
            self.projects = True
            self.contacts = True

    # ---------------------------------------------------------
    # Helper: Delete Stock Pickings safely
    # ---------------------------------------------------------
    def _force_delete_pickings(self, pickings):
        if not pickings:
            return

        move_lines = pickings.mapped("move_line_ids")
        moves = pickings.mapped("move_ids")

        move_lines.write({"state": "draft", "quantity": 0})
        move_lines.unlink()

        moves.write({"state": "draft"})
        moves.unlink()

        pickings.write({"state": "draft"})
        pickings.unlink()

    # ---------------------------------------------------------
    # Helper: Delete Invoices safely
    # ---------------------------------------------------------
    def _delete_invoices(self, move_types):
        moves = self.env["account.move"].search([("move_type", "in", move_types)])
        if not moves:
            return

        moves.mapped("line_ids").filtered("reconciled").remove_move_reconcile()
        moves.filtered(lambda m: m.state == "posted").button_draft()
        moves.filtered(lambda m: m.state == "cancel").button_draft()
        moves.unlink()

    # ---------------------------------------------------------
    # Main Action
    # ---------------------------------------------------------
    def action_clear_data(self):

        # 🔐 Security Check
        if not self.env.user.has_group("base.group_system"):
            raise UserError("Only administrators can perform this action.")

        # ── Sales ─────────────────────────────
        if self.sale:
            self._delete_invoices(["out_invoice", "out_refund"])

            sale_orders = self.env["sale.order"].search([])

            self._force_delete_pickings(sale_orders.mapped("picking_ids"))

            sale_orders.write({"state": "draft"})
            sale_orders.mapped("order_line").unlink()
            sale_orders.unlink()

        # ── Purchase ──────────────────────────
        if self.purchase:
            self._delete_invoices(["in_invoice", "in_refund"])

            purchase_orders = self.env["purchase.order"].search([])

            self._force_delete_pickings(purchase_orders.mapped("picking_ids"))

            purchase_orders.write({"state": "cancel"})
            purchase_orders.mapped("order_line").unlink()
            purchase_orders.unlink()

        # ── Inventory ─────────────────────────
        if self.inventory:
            all_pickings = self.env["stock.picking"].search([])
            self._force_delete_pickings(all_pickings)
            self.env["stock.quant"].search([]).unlink()

        # ── Projects ──────────────────────────
        if self.projects:
            tasks = self.env["project.task"].search([])
            tasks.write({"stage_id": False})
            tasks.unlink()
            self.env["project.project"].search([]).unlink()

        # ── Contacts ──────────────────────────
        if self.contacts:
            system_partner_ids = (
                self.env["res.users"].search([]).mapped("partner_id").ids
            )
            system_partner_ids += (
                self.env["res.company"].search([]).mapped("partner_id").ids
            )

            self.env["res.partner"].search(
                [("id", "not in", system_partner_ids)]
            ).unlink()

        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
