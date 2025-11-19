# 832工程数据库应用系统

为政府扶贫政策分析师提供脱贫案例库支持，整合县域访谈信息、宏观经济、农业结构、自然地理等数据。本项目基于中国人民大学应用经济学院"832工程"访谈数据开发。

## 🚀 快速启动

### 1. 启动后端
确保数据库已配置并运行（见下文数据库配置）。

```bash
# 安装依赖
pip install -r requirements.txt

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

**提示：** 如页面加载异常，请尝试强制刷新 (Cmd/Ctrl + Shift + R)。

---

## 📂 项目结构

```
db_lite/
├── backend/               # 后端代码
│   ├── app.py            # Flask应用入口
│   ├── db.py             # 数据库连接配置
│   ├── init_database.py  # 数据初始化脚本
│   └── api/              # API 路由模块
│       ├── compare.py    # 对比分析
│       ├── counties.py   # 县域查询
│       ├── interviews.py # 访谈记录
│       └── stats.py      # 全局统计
├── frontend/             # 前端代码
│   └── index.html        # 单页应用主文件 (包含HTML/CSS/JS)
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
- 展示访谈对象、时间、调研员信息及访谈摘要。

### 4. 对比分析 (Comparative Analysis)
- 多县数据横向对比。
- 经济发展趋势、农业产值结构的直观对比图表。

## 🛠 技术栈

### 后端
- **Python 3.8+**
- **Flask**: 轻量级Web框架
- **PyMySQL**: 数据库驱动
- **Pandas**: 数据处理

### 前端
- **HTML5 / CSS3 / JavaScript (ES6+)**
- **TailwindCSS**: 实用优先的CSS框架 (CDN引入)
- **FullPage.js**: 全屏滚动交互
- **Apache ECharts**: 交互式数据可视化
- **Font Awesome**: 图标库

## ⚙️ 配置说明

### 数据库配置
编辑 `backend/db.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password', # 修改为你的数据库密码
    'database': 'poverty_alleviation_832',
    'charset': 'utf8mb4'
}
```

### 数据初始化
首次运行需导入数据：
```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE poverty_alleviation_832 DEFAULT CHARACTER SET utf8mb4;"

# 2. 创建表结构
mysql -u root -p poverty_alleviation_832 < plan/05_create_tables.sql

# 3. 导入CSV数据
python backend/init_database.py
```

### 前端API地址
如果在非本地环境部署，需修改 `frontend/index.html` 中的 `API_BASE` 变量：
```javascript
// 约第 468 行
const API_BASE = 'http://your-server-ip:5001/api';
```

## 📚 数据库设计
- 遵循第三范式 (3NF)
- 包含县域基础信息、经济数据、农业数据、访谈记录等核心实体。
- 详细设计见 `plan/` 目录。
