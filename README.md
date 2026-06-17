# 装修预算与支出管理 API 服务

## Docker 启动

```bash
cp .env .env.local 2>/dev/null || true
docker compose up --build
```

- API 地址：http://localhost:19306/api/
- Swagger 地址：http://localhost:19306/api/schema/swagger-ui/
- DRF Browsable API：http://localhost:19306/api/budgets/

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端 | Django 5 + Django REST Framework |
| 认证 | djangorestframework-simplejwt |
| API 文档 | drf-spectacular |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 部署 | Docker Compose |

## 目录结构

```text
backend/
├── budget_app/
│   ├── views/
│   ├── serializers/
│   ├── services/
│   ├── middleware/
│   ├── filters/
│   ├── models.py
│   ├── permissions.py
│   ├── urls.py
│   └── admin.py
├── config/
└── manage.py
```

## 枚举位置

业务枚举集中定义在 `backend/budget_app/models.py` 的 `TextChoices` 中；同时按提示词保留 `backend/src/types/enums.ts` 作为跨端/文档对照。

## 核心接口

- `GET/POST /api/budgets/`
- `GET/POST /api/items/`
- `GET/POST /api/expenses/`
- `POST /api/expenses/{id}/submit/`
- `POST /api/expenses/{id}/approve/`
- `POST /api/expenses/{id}/reject/`
- `POST /api/expenses/{id}/resubmit/`
- `PATCH /api/expenses/{id}/update_rejected/`
- `GET /api/expenses/{id}/approval_history/`
- `POST /api/expenses/{id}/pay/`
- `GET/POST /api/suppliers/`
- `GET/POST /api/reconciliations/`

## 驳回后修改再提交流程

### 业务流程
1. **提交支出**：`POST /api/expenses/{id}/submit/` - 提交支出进入审批流程
2. **审批驳回**：`POST /api/expenses/{id}/reject/` - 审批人驳回并填写驳回意见
3. **修改信息**：`PATCH /api/expenses/{id}/update_rejected/` - 申请人修改 **金额、事由、供应商**
4. **重新提交**：`POST /api/expenses/{id}/resubmit/` - 重新提交审批，**原单号保留**
5. **查看历史**：`GET /api/expenses/{id}/approval_history/` - 查询完整审批历史意见

### 特性说明
- 已驳回状态仅允许修改：`amount`(金额)、`description`(事由)、`supplier`(供应商)
- 支出单号 `expense_no` 生成后永不改变，支持多次驳回修改重新提交
- `resubmission_count` 记录重新提交次数
- `approval_histories` 包含完整的审批历史记录（每次状态变更都有记录）
- 驳回时必须填写驳回意见

## License

MIT
