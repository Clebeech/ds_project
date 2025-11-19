# 管理员功能增强与数据库触发器设计

为了满足数据库课程对"系统管理"和"数据完整性"的高级要求，我们将为管理员(Admin)角色增加数据管理能力，并在数据库层引入**触发器(Trigger)**以实现自动化数据维护。

## 1. 功能需求分析

### 1.1 用户管理 (User Management)
*   **需求**：管理员可以创建新的分析师账号，以便分发给团队成员使用。
*   **操作**：输入用户名、密码，系统自动将其角色设为 `analyst`。
*   **权限**：仅 `admin` 角色可用。

### 1.2 数据录入 (Data Entry)
*   **需求**：管理员可以录入新的访谈记录。这是数据库系统中典型的 `INSERT` 操作。
*   **场景**：调研团队提交了新的访谈数据，管理员将其录入系统。
*   **权限**：仅 `admin` 角色可用。

### 1.3 数据库自动化 (Database Automation) - **课程加分项**
*   **需求**：当新增一条访谈记录时，系统应自动更新对应调研员的"已完成访谈次数"。
*   **实现方式**：**数据库触发器 (Trigger)**。
*   **逻辑**：`AFTER INSERT ON interviews` -> `UPDATE surveyors SET CompletedInterviews = CompletedInterviews + 1`。

---

## 2. 数据库设计变更

### 2.1 新增触发器 (Trigger)

我们将创建一个触发器 `trg_update_interview_count`。

```sql
DELIMITER //
CREATE TRIGGER trg_update_interview_count
AFTER INSERT ON interviews
FOR EACH ROW
BEGIN
    -- 当插入新访谈时，自动增加对应调研员的完成计数
    UPDATE surveyors 
    SET CompletedInterviews = CompletedInterviews + 1
    WHERE SurveyorID = NEW.SurveyorID;
END;//
DELIMITER ;
```

*   *注：如果还需要处理删除操作，可以再加一个 `AFTER DELETE` 触发器。*

---

## 3. API 接口设计

### 3.1 创建用户接口
*   **URL**: `POST /api/admin/users`
*   **Auth**: `@admin_required`
*   **Body**: `{ "username": "...", "password": "..." }`
*   **Response**: `{ "success": true, "user_id": ... }`

### 3.2 录入访谈接口
*   **URL**: `POST /api/interviews`
*   **Auth**: `@admin_required` (暂定仅管理员可录入，也可开放给分析师)
*   **Body**: 
    ```json
    {
        "surveyor_id": "S2021001",
        "county_code": "130125",
        "interviewee_name": "张三",
        "content": "访谈内容...",
        "date": "2023-10-01",
        "quality": 5.0
    }
    ```

---

## 4. 前端设计 (Admin Dashboard)

在前端增加一个仅管理员可见的悬浮按钮或菜单项"管理面板"，点击后弹出模态框。

### 4.1 管理面板功能区
1.  **用户管理 Tab**：
    *   简单的表单：用户名、密码 -> [创建分析师] 按钮。
    *   (可选) 用户列表展示。

2.  **数据录入 Tab**：
    *   访谈录入表单：选择县(支持搜索)、输入调研员ID、内容等。

---

## 5. 实施计划

1.  **数据库层**：执行 SQL 创建触发器。
2.  **后端层**：实现 `create_user` 和 `create_interview` 接口。
3.  **前端层**：
    *   扩展 `updateUserUI` 逻辑，管理员登录后显示"管理面板"按钮。
    *   制作管理面板 Modal。
    *   对接后端接口。

