from datetime import date

from django.db import transaction
from rest_framework.exceptions import ValidationError

from budget_app.models import (
    ApprovalAction,
    ApprovalHistory,
    AuditLog,
    ExpenseRecord,
    ExpenseStatus,
)
from budget_app.services.balance_calculator import BalanceCalculator


class ExpenseService:
    def __init__(self) -> None:
        self.calculator = BalanceCalculator()

    @transaction.atomic
    def submit(self, expense: ExpenseRecord, actor_id: str) -> ExpenseRecord:
        if expense.status != ExpenseStatus.DRAFT:
            raise ValidationError("只有草稿支出可以提交审批。")
        return self._transition(
            expense,
            ExpenseStatus.SUBMITTED,
            actor_id,
            ApprovalAction.SUBMIT,
            "expense.submit",
        )

    @transaction.atomic
    def approve(self, expense: ExpenseRecord, actor_id: str, comment: str = "") -> ExpenseRecord:
        if expense.status != ExpenseStatus.SUBMITTED:
            raise ValidationError("只有已提交支出可以审批。")
        expense.approver_id = actor_id
        expense.approval_comment = comment
        updated = self._transition(
            expense,
            ExpenseStatus.APPROVED,
            actor_id,
            ApprovalAction.APPROVE,
            "expense.approve",
            comment,
        )
        self.calculator.recalculate_item(updated.budget_item)
        self.calculator.recalculate_sheet(updated.budget_item.budget_sheet)
        return updated

    @transaction.atomic
    def reject(self, expense: ExpenseRecord, actor_id: str, comment: str = "") -> ExpenseRecord:
        if expense.status != ExpenseStatus.SUBMITTED:
            raise ValidationError("只有已提交支出可以驳回。")
        if not comment:
            raise ValidationError("驳回必须填写驳回意见。")
        expense.approver_id = actor_id
        expense.approval_comment = comment
        return self._transition(
            expense,
            ExpenseStatus.REJECTED,
            actor_id,
            ApprovalAction.REJECT,
            "expense.reject",
            comment,
        )

    @transaction.atomic
    def resubmit(self, expense: ExpenseRecord, actor_id: str) -> ExpenseRecord:
        if expense.status != ExpenseStatus.REJECTED:
            raise ValidationError("只有已驳回支出可以重新提交。")
        expense.resubmission_count += 1
        return self._transition(
            expense,
            ExpenseStatus.SUBMITTED,
            actor_id,
            ApprovalAction.RESUBMIT,
            "expense.resubmit",
        )

    @transaction.atomic
    def update_rejected(
        self,
        expense: ExpenseRecord,
        actor_id: str,
        amount: float | None = None,
        description: str | None = None,
        supplier_id: int | None = None,
    ) -> ExpenseRecord:
        if expense.status != ExpenseStatus.REJECTED:
            raise ValidationError("只有已驳回支出可以编辑修改。")

        before = {}
        if amount is not None:
            before["amount"] = str(expense.amount)
            expense.amount = amount
        if description is not None:
            before["description"] = expense.description
            expense.description = description
        if supplier_id is not None:
            before["supplier_id"] = expense.supplier_id
            from budget_app.models import Supplier

            expense.supplier = Supplier.objects.get(id=supplier_id)

        if before:
            expense.save()
            AuditLog.objects.create(
                actor_id=actor_id,
                action="expense.update_rejected",
                entity_type="ExpenseRecord",
                entity_id=str(expense.id),
                before=before,
                after={
                    k: str(getattr(expense, k) if k != "supplier_id" else expense.supplier_id)
                    for k in before
                },
            )

        return expense

    @transaction.atomic
    def pay(self, expense: ExpenseRecord, actor_id: str) -> ExpenseRecord:
        if expense.status != ExpenseStatus.APPROVED:
            raise ValidationError("只有已审批支出可以确认付款。")
        expense.paid_at = date.today()
        return self._transition(
            expense,
            ExpenseStatus.PAID,
            actor_id,
            ApprovalAction.PAY,
            "expense.pay",
        )

    def _transition(
        self,
        expense: ExpenseRecord,
        status: str,
        actor_id: str,
        action: str,
        audit_action: str,
        comment: str = "",
    ) -> ExpenseRecord:
        before = {"status": expense.status}
        previous_status = expense.status
        expense.status = status
        expense.save()

        version = expense.approval_histories.count() + 1
        ApprovalHistory.objects.create(
            expense=expense,
            action=action,
            actor_id=actor_id,
            comment=comment,
            previous_status=previous_status,
            new_status=status,
            version=version,
        )

        self.calculator.recalculate_sheet(expense.budget_item.budget_sheet)
        AuditLog.objects.create(
            actor_id=actor_id,
            action=audit_action,
            entity_type="ExpenseRecord",
            entity_id=str(expense.id),
            before=before,
            after={"status": expense.status},
        )
        return expense
