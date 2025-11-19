# 用户认证与权限系统设计方案

## 1. 需求分析

为了满足数据库系统概论课程对"用户区分"和"安全性"的要求，我们将系统用户划分为三类，并引入登录机制。

### 1.1 用户角色定义

| 角色 | 权限描述 | 典型场景 |
| :--- | :--- | :--- |
| **游客 (Guest)** | **有限只读权限**。<br>只能查看宏观统计数据和县域列表基础信息。<br>🚫 **不可见**：详细访谈内容（隐私保护）、对比分析工具（高级功能）。 | 公众访问，了解832工程概况。 |
| **分析师 (Analyst)** | **完整只读权限**。<br>查看所有数据，包括详细访谈记录、使用对比分析工具、导出数据。 | 政策研究员进行深度分析。 |
| **管理员 (Admin)** | **系统管理权限**。<br>包含分析师所有权限，额外拥有：<br>1. **用户管理**：添加/删除分析师账号。<br>2. **日志审计**：查看用户登录日志。<br>3. **数据维护**：(预留) 触发数据更新脚本。 | 课程助教或系统维护者。 |

### 1.2 交互流程
1. **系统入口**：用户访问首页，默认展示"登录页"或"包含受限内容的公开页"。建议采用**登录遮罩(Login Modal)**，未登录时背景模糊或只显示Hero Section。
2. **登录验证**：输入账号密码 -> 后端验证 -> 返回Token/Session -> 前端存储用户状态。
3. **权限控制**：
   - **前端**：根据角色隐藏/显示导航栏菜单（如：游客看不到"对比分析"入口）。
   - **后端**：API接口增加权限校验装饰器（如 `@login_required`），防止直接调用接口绕过前端限制。

---

## 2. 数据库设计 (Database Schema)

新增两张表：`users` (用户表) 和 `access_logs` (访问日志表 - 满足审计需求)。

### 2.1 用户表 (users)

```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    role ENUM('admin', 'analyst', 'guest') NOT NULL DEFAULT 'guest' COMMENT '角色',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_login TIMESTAMP NULL COMMENT '最后登录时间'
) COMMENT='系统用户表';
```

### 2.2 访问日志表 (access_logs)
*用于记录登录行为，体现数据库审计功能。*

```sql
CREATE TABLE access_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '关联用户ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型：LOGIN, LOGOUT, VIEW_SENSITIVE',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='用户访问日志';
```

---

## 3. API 接口设计

在 `backend/api/` 下新增 `auth.py` 模块。

### 3.1 认证接口
| 方法 | 路径 | 功能 | 参数 | 返回 |
| :--- | :--- | :--- | :--- | :--- |
| POST | `/api/auth/login` | 用户登录 | `username`, `password` | `token`, `role`, `user_info` |
| POST | `/api/auth/logout` | 登出 | - | `success` |
| GET | `/api/auth/me` | 获取当前用户信息 | - | `user_info` |

### 3.2 管理接口 (Admin Only)
| 方法 | 路径 | 功能 | 参数 |
| :--- | :--- | :--- | :--- |
| POST | `/api/admin/users` | 创建新用户 | `username`, `password`, `role` |
| GET | `/api/admin/logs` | 查看系统日志 | - |

---

## 4. 前端修改方案

### 4.1 界面状态
使用 `localStorage` 存储 `user_role`。

1. **未登录/游客状态**：
   - 顶部导航栏显示 "登录" 按钮。
   - **Section 5 (访谈记录)**：显示模糊遮罩，提示 "请登录分析师账号查看详细访谈"。
   - **Section 6 (对比分析)**：隐藏或禁用，提示 "高级功能需登录"。

2. **分析师状态**：
   - 顶部显示 "欢迎, [用户名]" 及 "退出" 按钮。
   - 解锁所有 Section。

3. **管理员状态**：
   - 顶部增加 "管理后台" 入口（点击弹出模态框显示用户列表和日志）。

### 4.2 文件结构变动
- `backend/api/auth.py`: 新增认证逻辑。
- `backend/utils/security.py`: 密码哈希工具 (使用 `werkzeug.security`)。
- `frontend/index.html`: 增加登录模态框 HTML。
- `frontend/js/auth.js` (新建或内嵌): 处理登录请求、Token存储、UI状态切换。

---

## 5. 实施路线图 (Implementation Plan)

1.  **数据库层**：执行 SQL 建表脚本，插入默认管理员账号 (`admin`/`admin123`)。
2.  **后端层**：
    - 引入 `werkzeug.security` 进行密码哈希。
    - 实现 `auth` 蓝图。
    - 为 `interviews` 和 `compare` 接口添加权限检查。
3.  **前端层**：
    - 编写登录界面（Modal）。
    - 实现 AJAX 登录逻辑。
    - 实现基于角色的 UI 渲染函数 `renderByRole(role)`。
4.  **测试**：验证游客无法访问受限接口，验证管理员可以创建用户。

