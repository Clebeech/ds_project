# 832工程数据库应用系统

为政府扶贫政策分析师提供脱贫案例库支持，整合县域访谈信息、宏观经济、农业结构、自然地理等数据。本项目基于中国人民大学应用经济学院"832工程"访谈数据开发。

## 🚀 快速启动

### 1. 启动后端
确保数据库已配置并运行。

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化认证系统 (创建用户表和默认账号)
python backend/init_auth.py

# 启动API服务 (默认端口 5001)
python run.py
```

### 2. 启动前端
```bash
cd frontend
# 启动静态文件服务 (默认端口 8000)
python -m http.server 8000
```

### 3. 访问应用
打开浏览器访问：[http://localhost:8000](http://localhost:8000)

---

## 🔐 用户权限说明

系统包含用户认证模块，区分不同角色的访问权限：

| 角色 | 账号 / 密码 | 权限范围 |
| :--- | :--- | :--- |
| **游客** | (无需登录) | 查看宏观统计、县域列表。**无法查看**详细访谈内容和对比分析工具。 |
| **分析师** | `analyst` / `analyst123` | 拥有完整数据访问权限，可使用对比分析工具。 |
| **调研员** | `surveyor` / `surveyor123` | 拥有**数据录入**权限 (工作台)，可新增访谈记录。 |
| **管理员** | `admin` / `admin123` | 拥有所有权限，包括创建新分析师账号。 |

> **提示**：在页面右上角点击"登录"按钮进行认证。

---

## 📂 项目结构

```
db_lite/
├── backend/               # 后端代码
│   ├── app.py            # Flask应用入口
│   ├── db.py             # 数据库连接配置
│   ├── init_auth.py      # 认证系统初始化
│   ├── init_database.py  # 数据导入脚本
│   ├── init_views.py      # 数据库视图初始化
│   ├── init_procedures.py # 存储过程初始化
│   ├── init_triggers.py   # 触发器初始化
│   └── api/              # API 路由模块
│       ├── auth.py       # 用户认证
│       ├── counties.py   # 县域数据 (使用视图和存储过程)
│       ├── compare.py    # 对比分析 (需登录)
│       ├── interviews.py # 访谈记录 (详情需登录)
│       ├── surveyors.py  # 调研员数据 (使用视图和存储过程)
│       ├── stats.py      # 统计数据 (复杂查询)
│       ├── export.py     # 数据导出功能
│       └── views_demo.py # 视图演示接口
├── frontend/             # 前端代码
│   └── index.html        # 单页应用主文件
├── data/                 # 原始CSV数据文件
├── plan/                 # 数据库设计文档与SQL脚本
│   ├── 13_create_views.sql      # 视图创建SQL
│   ├── 14_create_procedures.sql # 存储过程创建SQL
│   └── 15_implementation_summary.md # 实施总结
└── requirements.txt      # Python依赖列表
```

## ✨ 功能模块

### 1. 数据概览 (Dashboard)
- 系统核心指标展示：覆盖832个贫困县，包含访谈记录、调研员数据等。
- 宏观数据可视化：贫困县地理分布地图、访谈关键词词云。
- 实时统计：县域数量、访谈记录、调研团队等核心指标。

### 2. 县域探索 (County Explorer)
- **列表与筛选**：支持按地区、省份筛选县域，支持关键词搜索。
- **县域详情**：
  - 经济指标趋势：GDP、财政收支变化。
  - 农业结构分析：农林牧渔产值占比。
  - 词云展示：基于访谈内容的关键词提取。
- **综合报告**：使用存储过程生成县域完整报告（经济、农业、访谈等全方位数据）。
- **数据导出**：支持导出县域数据为CSV格式（需登录）。

### 3. 访谈记录 (Interview Archive)
- 完整的访谈数据库，支持全文搜索和高级筛选。
- **权限控制**：游客仅可见摘要，详细内容需登录分析师账号查看。
- **词云分析**：自动提取访谈关键词，生成可视化词云。
- **数据导出**：支持导出访谈记录为CSV格式（需登录）。

### 4. 对比分析 (Comparative Analysis)
- **(高级功能 - 需登录)** 多县数据横向对比。
- 经济发展趋势、农业产值结构的直观对比图表。
- 支持折线图、柱状图、面积图等多种可视化方式。

### 5. 调研团队 (Survey Team)
- 调研员信息展示：团队结构、工作统计、负责县域。
- **工作绩效**：使用存储过程分析调研员工作绩效（访谈次数、完成率、覆盖范围等）。
- **数据导出**：支持导出调研员数据为CSV格式（需登录）。

### 6. 数据导出功能
- **县域数据导出**：支持按地区、摘帽年份筛选后导出。
- **访谈记录导出**：支持按县域、调研员筛选后导出。
- **调研员数据导出**：导出完整的调研团队信息。
- 所有导出功能需要登录，文件格式为CSV。

## 🛠 技术栈

- **后端**: Python (Flask), PyMySQL, Pandas, Jieba (中文分词)
- **前端**: HTML5, TailwindCSS, FullPage.js, ECharts, ECharts WordCloud
- **数据库**: MySQL (符合3NF设计)
  - **视图 (VIEW)**: 简化复杂查询，提高代码复用性
  - **存储过程 (STORED PROCEDURE)**: 封装业务逻辑，提高执行效率
  - **触发器 (TRIGGER)**: 自动维护统计数据

## ⚙️ 配置说明

### 数据库配置
编辑 `backend/db.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password', 
    'database': 'poverty_alleviation_832',
    'charset': 'utf8mb4'
}
```

### 数据初始化
```bash
# 1. 创建数据库和业务表
mysql -u root -p -e "CREATE DATABASE poverty_alleviation_832 DEFAULT CHARACTER SET utf8mb4;"
mysql -u root -p poverty_alleviation_832 < plan/05_create_tables.sql

# 2. 导入业务数据
python backend/init_database.py

# 3. 初始化认证表和默认用户
python backend/init_auth.py

# 4. 创建数据库视图（简化查询）
python backend/init_views.py

# 5. 创建存储过程（封装业务逻辑）
python backend/init_procedures.py

# 6. 创建触发器（自动维护统计）
python backend/init_triggers.py
```

---

## 🗄️ 数据库系统特性

本项目从数据库系统课程的角度，实现了完整的数据库功能：

### 1. 数据库视图 (VIEW)
- **`v_county_complete_info`**: 县域完整信息视图（整合基础信息、经济、农业、访谈统计）
- **`v_surveyor_work_statistics`**: 调研员工作统计视图（整合调研员信息、负责县域、访谈统计）
- **`v_poverty_county_summary`**: 贫困县汇总视图（整合贫困县信息、摘帽状态、经济指标变化）

**优势**：
- 简化复杂查询：API代码从20+行SQL简化为3行
- 提高代码复用性：多个接口共享视图定义
- 易于维护：修改视图定义即可影响所有使用它的查询

### 2. 存储过程 (STORED PROCEDURE)
- **`sp_get_county_comprehensive_report`**: 生成县域综合报告
- **`sp_statistics_by_region`**: 按地区统计分析
- **`sp_get_surveyor_performance`**: 获取调研员工作绩效分析

**优势**：
- 业务逻辑封装在数据库层
- 减少网络传输，提高执行效率
- 参数化查询，灵活高效

### 3. 触发器 (TRIGGER)
- **`trg_update_interview_count`**: 自动更新调研员的访谈统计

**优势**：
- 自动化数据维护
- 保证数据一致性
- 减少应用层代码复杂度

### 4. 复杂查询示例
- **HAVING子句**: 找出访谈次数超过平均值的调研员
- **子查询嵌套**: 查找摘帽后GDP增长最快的县
- **窗口函数**: 计算各县GDP排名和增长率

### 5. 数据导出功能
- 支持CSV格式导出
- 支持按条件筛选后导出
- 权限控制：仅登录用户可使用

---

## 📡 API接口说明

### 核心接口
- `GET /api/counties` - 获取县域列表（使用视图）
- `GET /api/counties/<code>/report` - 获取县域综合报告（使用存储过程）
- `GET /api/interviews` - 获取访谈记录
- `GET /api/interviews/wordcloud` - 获取访谈词云数据
- `GET /api/surveyors` - 获取调研员列表（使用视图）
- `GET /api/surveyors/<id>/performance` - 获取调研员绩效（使用存储过程）
- `GET /api/stats/region?region=xxx` - 地区统计分析（使用存储过程）
- `GET /api/stats/complex/above-average` - 复杂查询示例（HAVING子句）
- `GET /api/stats/complex/top-gdp-growth` - 复杂查询示例（子查询嵌套）

### 数据导出接口（需登录）
- `GET /api/export/counties` - 导出县域数据
- `GET /api/export/interviews` - 导出访谈记录
- `GET /api/export/surveyors` - 导出调研员数据

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/register` - 创建新用户（仅管理员）
