# 调研员角色设计

为了完善数据采集流程，我们引入**调研员 (Surveyor)** 角色。

## 1. 角色定义

| 角色 | 权限描述 | 典型场景 |
| :--- | :--- | :--- |
| **调研员 (Surveyor)** | **数据录入权限**。<br>1. **可以**：录入新的访谈记录。<br>2. **可以**：查看基础数据。<br>3. **不可**：创建用户、管理系统。 | 一线调研人员，负责将田野调查数据上传至系统。 |

## 2. 数据库变更

需要修改 `users` 表的 `role` 枚举类型。

```sql
ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'analyst', 'surveyor', 'guest') NOT NULL DEFAULT 'guest';
```

## 3. 功能实现

### 3.1 后端鉴权
*   修改 `@admin_required` 装饰器或新增 `@surveyor_required`。
*   更推荐的方式：修改 `create_interview` 接口的权限检查，允许 `admin` OR `surveyor`。

### 3.2 前端调整
*   当用户角色为 `surveyor` 时：
    *   显示 "⚙️ 工作台" 按钮（类似于管理员的"管理"按钮）。
    *   打开模态框时，**仅显示** "数据录入" Tab，隐藏 "用户管理" Tab。

## 4. 实施步骤

1.  **数据库**：更新 `role` 字段定义。
2.  **后端**：
    *   更新 `init_auth.py` 添加默认调研员账号 (`surveyor` / `surveyor123`)。
    *   更新 `api/interviews.py`，允许 `surveyor` 角色调用 `POST /api/interviews`。
3.  **前端**：
    *   更新 UI 逻辑，识别 `surveyor` 角色并展示相应界面。

