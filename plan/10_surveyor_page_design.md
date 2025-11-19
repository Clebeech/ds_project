# 调研员 (Surveyors) 页面设计

为了展示 `surveyors` 表的信息，我们将新增一个专门的"调研团队"页面（Section）。

## 1. 需求分析

### 1.1 展示内容
根据 `surveyors.csv` 和 `plan/05_create_tables.sql`，调研员信息包含：
*   **基础信息**：姓名 (Name)、性别 (Gender)、所属院系 (Department)、学历 (Education)、专业 (Major)
*   **团队信息**：所属分队 (TeamID)、负责县域 (CountyCode)、调研角色 (Role)
*   **任务进度**：已完成访谈 (CompletedInterviews)、待补访 (PendingInterviews)
*   **其他**：专长 (Expertise)、备注 (Notes)

### 1.2 展示形式
*   **列表页 (Card Grid)**：以卡片形式展示调研员头像（可用占位符）、姓名、角色、负责县域、完成访谈数。
*   **详情模态框 (Detail Modal)**：点击卡片后弹出，展示详细信息（联系方式、专长、备注等）。**注：联系电话和邮箱应脱敏或仅管理员/分析师可见。**
*   **筛选/搜索**：支持按姓名、分队、县域搜索。

## 2. 数据库操作
我们需要一个后端接口来获取调研员数据。

*   `GET /api/surveyors`
    *   Params: `page`, `limit`, `keyword` (姓名/ID), `county_code`
    *   Response: List of surveyors (关联 CountyName)

## 3. 前端设计
在 `index.html` 中新增一个 Section (Section 7)，位于"对比分析"之后。

### 3.1 UI 布局
*   **标题**：调研团队 (Survey Team)
*   **统计栏**：总人数、覆盖县域数、累计访谈数。
*   **筛选栏**：搜索框、分队筛选。
*   **卡片墙**：响应式 Grid 布局。

### 3.2 卡片设计
```html
<div class="surveyor-card">
  <div class="avatar">...</div>
  <h3>张明 <span class="role-badge">分队负责人</span></h3>
  <p>负责县域：安徽省 岳西县</p>
  <p>已访谈：35次</p>
</div>
```

## 4. 实施步骤
1.  **后端**：创建 `backend/api/surveyors.py`，实现查询接口。
2.  **注册**：在 `app.py` 中注册新蓝图。
3.  **前端**：
    *   修改 `index.html` HTML 结构，添加新 Section。
    *   添加 JS 逻辑：`loadSurveyors()`。
    *   添加 CSS 样式。

## 5. 隐私保护 (Privacy)
*   对于游客 (Guest)，隐藏 `Phone` 和 `Email` 字段。
*   后端接口应根据当前登录用户的 `role` 动态过滤敏感字段。

