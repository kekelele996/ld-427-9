from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from budget_app.filters.expense_filter import ExpenseRecordFilter
from budget_app.models import ExpenseRecord, ExpenseStatus
from budget_app.permissions import BudgetRBACPermission
from budget_app.serializers.expense_serializer import (
    ApprovalHistorySerializer,
    ExpenseRecordSerializer,
    RejectedExpenseUpdateSerializer,
)
from budget_app.services.expense_service import ExpenseService


class ExpenseRecordViewSet(viewsets.ModelViewSet):
    queryset = ExpenseRecord.objects.select_related(
        "budget_item", "supplier", "budget_item__budget_sheet"
    ).prefetch_related("approval_histories")
    serializer_class = ExpenseRecordSerializer
    permission_classes = [BudgetRBACPermission]
    filterset_class = ExpenseRecordFilter

    def get_serializer_class(self):
        if self.action == "update_rejected":
            return RejectedExpenseUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ExpenseStatus.REJECTED:
            return self.update_rejected(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        expense = ExpenseService().submit(self.get_object(), str(request.user.id or "system"))
        return Response(self.get_serializer(expense).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        self.approval_action = True
        expense = ExpenseService().approve(
            self.get_object(),
            str(request.user.id or "system"),
            request.data.get("approval_comment", ""),
        )
        return Response(self.get_serializer(expense).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        self.approval_action = True
        expense = ExpenseService().reject(
            self.get_object(),
            str(request.user.id or "system"),
            request.data.get("reject_comment", ""),
        )
        return Response(self.get_serializer(expense).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def resubmit(self, request, pk=None):
        expense = ExpenseService().resubmit(self.get_object(), str(request.user.id or "system"))
        return Response(self.get_serializer(expense).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def update_rejected(self, request, pk=None):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        expense = ExpenseService().update_rejected(
            instance,
            str(request.user.id or "system"),
            amount=request.data.get("amount"),
            description=request.data.get("description"),
            supplier_id=request.data.get("supplier"),
        )
        return Response(ExpenseRecordSerializer(expense).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def approval_history(self, request, pk=None):
        expense = self.get_object()
        histories = expense.approval_histories.all()
        serializer = ApprovalHistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        self.accounting_action = True
        expense = ExpenseService().pay(self.get_object(), str(request.user.id or "system"))
        return Response(self.get_serializer(expense).data, status=status.HTTP_200_OK)
