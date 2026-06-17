from rest_framework import serializers

from budget_app.models import ApprovalHistory, ExpenseRecord, ExpenseStatus


class ApprovalHistorySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    previous_status_display = serializers.CharField(source="get_previous_status_display", read_only=True)
    new_status_display = serializers.CharField(source="get_new_status_display", read_only=True)

    class Meta:
        model = ApprovalHistory
        fields = [
            "id",
            "action",
            "action_display",
            "actor_id",
            "comment",
            "previous_status",
            "previous_status_display",
            "new_status",
            "new_status_display",
            "version",
            "created_at",
        ]
        read_only_fields = fields


class RejectedExpenseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseRecord
        fields = ["amount", "description", "supplier"]

    def validate(self, attrs):
        if self.instance and self.instance.status != ExpenseStatus.REJECTED:
            raise serializers.ValidationError("只有已驳回的支出可以编辑修改。")
        return attrs


class ExpenseRecordSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)
    approval_histories = ApprovalHistorySerializer(many=True, read_only=True)
    editable_fields = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseRecord
        fields = [
            "id",
            "expense_no",
            "budget_item",
            "amount",
            "expense_date",
            "payment_method",
            "payment_method_display",
            "supplier",
            "invoice_no",
            "description",
            "attachment_url",
            "status",
            "status_display",
            "applicant_id",
            "approver_id",
            "approval_comment",
            "paid_at",
            "resubmission_count",
            "approval_histories",
            "editable_fields",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "approver_id",
            "approval_comment",
            "paid_at",
            "created_at",
            "updated_at",
            "expense_no",
            "resubmission_count",
            "status_display",
            "payment_method_display",
            "approval_histories",
            "editable_fields",
        ]

    def get_editable_fields(self, obj):
        if obj.status == ExpenseStatus.DRAFT:
            return [
                "budget_item",
                "amount",
                "expense_date",
                "payment_method",
                "supplier",
                "invoice_no",
                "description",
                "attachment_url",
            ]
        elif obj.status == ExpenseStatus.REJECTED:
            return ["amount", "description", "supplier"]
        return []

    def update(self, instance, validated_data):
        if instance.status not in [ExpenseStatus.DRAFT, ExpenseStatus.REJECTED]:
            raise serializers.ValidationError("当前状态不允许修改。")

        if instance.status == ExpenseStatus.REJECTED:
            allowed_fields = {"amount", "description", "supplier"}
            invalid_fields = set(validated_data.keys()) - allowed_fields
            if invalid_fields:
                raise serializers.ValidationError(
                    f"已驳回状态仅允许修改字段: {', '.join(allowed_fields)}。"
                )

        return super().update(instance, validated_data)
