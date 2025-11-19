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
│   └── api/              # API 路由模块
│       ├── auth.py       # 用户认证
│       ├── compare.py    # 对比分析 (需登录)
│       ├── interviews.py # 访谈记录 (详情需登录)
│       └── ...
├── frontend/             # 前端代码
│   └── index.html        # 单页应用主文件
├── data/                 # 原始CSV数据文件
├── plan/                 # 数据库设计文档与SQL脚本
└── requirements.txt      # Python依赖列表
```

## ✨ 功能模块

### 1. 数据概览 (Dashboard)
- 系统核心指标展示：覆盖832个贫困县，包含访谈记录、调研员数据等。
- 宏观数据可视化：贫困县分布与状态概览。

### 2. 县域探索 (County Explorer)
- **列表与筛选**：支持按地区、省份筛选县域，支持关键词搜索。
- **县域详情**：
  - 经济指标趋势：GDP、财政收支变化。
  - 农业结构分析：农林牧渔产值占比。
  - 词云展示：基于访谈内容的关键词提取。

### 3. 访谈记录 (Interview Archive)
- 完整的访谈数据库，支持全文搜索。
- **权限控制**：游客仅可见摘要，详细内容需登录分析师账号查看。

### 4. 对比分析 (Comparative Analysis)
- **(高级功能 - 需登录)** 多县数据横向对比。
- 经济发展趋势、农业产值结构的直观对比图表。

## 🛠 技术栈

- **后端**: Python (Flask), PyMySQL, Pandas
- **前端**: HTML5, TailwindCSS, FullPage.js, ECharts
- **数据库**: MySQL (符合3NF设计)

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
```
