import django.db.models.deletion
from django.db import migrations, models

from budget_app.models import generate_expense_no


class Migration(migrations.Migration):
    dependencies = [
        ("budget_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="expenserecord",
            name="expense_no",
            field=models.CharField(
                default=generate_expense_no,
                editable=False,
                max_length=32,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="expenserecord",
            name="resubmission_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="ApprovalHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("Submit", "提交"),
                            ("Approve", "审批通过"),
                            ("Reject", "驳回"),
                            ("Resubmit", "重新提交"),
                            ("Pay", "确认付款"),
                        ],
                        max_length=24,
                    ),
                ),
                ("actor_id", models.CharField(max_length=64)),
                ("comment", models.TextField(blank=True, default="")),
                (
                    "previous_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Draft", "草稿"),
                            ("Submitted", "已提交"),
                            ("Approved", "已审批"),
                            ("Rejected", "已驳回"),
                            ("Paid", "已付款"),
                        ],
                        default="",
                        max_length=24,
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        choices=[
                            ("Draft", "草稿"),
                            ("Submitted", "已提交"),
                            ("Approved", "已审批"),
                            ("Rejected", "已驳回"),
                            ("Paid", "已付款"),
                        ],
                        max_length=24,
                    ),
                ),
                ("version", models.PositiveIntegerField(default=1)),
                (
                    "expense",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="approval_histories",
                        to="budget_app.expenserecord",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
