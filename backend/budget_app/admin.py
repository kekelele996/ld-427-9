from django.contrib import admin

from budget_app.models import (
    ApprovalHistory,
    AuditLog,
    BudgetItem,
    BudgetSheet,
    ExpenseRecord,
    Reconciliation,
    Supplier,
    UserRole,
)


@admin.register(BudgetSheet)
class BudgetSheetAdmin(admin.ModelAdmin):
    list_display = ("id", "project_id", "name", "total_amount", "spent_amount", "frozen_amount", "status", "version")
    list_filter = ("status", "project_id")
    search_fields = ("name", "project_id")


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ("id", "budget_sheet", "category", "subcategory_name", "budget_amount", "spent_amount")
    list_filter = ("category",)


@admin.register(ExpenseRecord)
class ExpenseRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "expense_no", "budget_item", "amount", "expense_date", "supplier", "status", "resubmission_count")
    list_filter = ("status", "payment_method")
    search_fields = ("expense_no",)
    readonly_fields = ("expense_no", "resubmission_count")


@admin.register(ApprovalHistory)
class ApprovalHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "expense", "action", "actor_id", "previous_status", "new_status", "version", "created_at")
    list_filter = ("action", "previous_status", "new_status")
    search_fields = ("expense__expense_no", "actor_id", "comment")
    readonly_fields = ("version",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "status", "rating", "contact_name", "phone")
    list_filter = ("category", "status", "rating")


@admin.register(Reconciliation)
class ReconciliationAdmin(admin.ModelAdmin):
    list_display = ("id", "project_id", "period_month", "supplier", "payable_amount", "paid_amount", "status")
    list_filter = ("status", "period_month")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor_id", "action", "entity_type", "entity_id", "created_at")
    list_filter = ("action", "entity_type")


admin.site.register(UserRole)
