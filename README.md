# 832工程数据库应用系统

为政府扶贫政策分析师提供脱贫案例库支持，整合县域访谈信息、宏观经济、农业结构、自然地理等数据。

## 项目结构

```
db_lite/
├── backend/           # 后端代码
│   ├── app.py        # Flask主应用
│   ├── db.py         # 数据库连接
│   ├── init_database.py  # 数据导入脚本
│   └── api/          # API路由
├── frontend/         # 前端页面
│   ├── index.html    # 主页面
│   └── app.js        # 前端逻辑
├── data/             # CSV数据文件
├── plan/             # 数据库设计文档
└── requirements.txt  # Python依赖
```

## 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 确保MySQL已安装并运行
```

### 2. 数据库初始化

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE poverty_alleviation_832 DEFAULT CHARACTER SET utf8mb4;"

# 执行建表脚本
mysql -u root -p poverty_alleviation_832 < plan/05_create_tables.sql

# 导入数据
python backend/init_database.py
```

### 3. 配置数据库连接

编辑 `backend/db.py`，修改数据库配置：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'poverty_alleviation_832',
    'charset': 'utf8mb4'
}
```

### 4. 启动后端API

```bash
# 方式1：使用启动脚本（推荐）
python run.py

# 方式2：直接运行
python -m backend.app
```

API将在 `http://localhost:5001` 启动

### 5. 打开前端页面

```bash
cd frontend
python -m http.server 8000
```

在浏览器访问 `http://localhost:8000`

**提示：** 如果页面显示异常，请强制刷新浏览器缓存：
- **Mac**: 按 `Cmd + Shift + R`
- **Windows/Linux**: 按 `Ctrl + Shift + R` 或 `Ctrl + F5`
- 或者打开开发者工具（F12），右键点击刷新按钮，选择"清空缓存并硬性重新加载"

## 功能模块

### 后端API

- **县域数据API**：查询县列表、详情、经济、农业、人口数据
- **访谈记录API**：查询访谈列表、详情、统计
- **对比分析API**：多县对比经济、农业、趋势数据
- **统计数据API**：系统概览统计

详细API文档见 [README_api.md](README_api.md)

### 前端页面

- **Hero页面**：超大数字展示，核心信息
- **数据概览**：系统统计信息
- **县域探索**：县列表、筛选、搜索
- **县域详情**：经济、农业数据可视化
- **访谈记录**：访谈列表、搜索
- **对比分析**：多县数据对比

## 技术栈

### 后端
- Python 3.8+
- Flask 2.3+
- PyMySQL
- Pandas

### 前端
- HTML5
- TailwindCSS 3.0+
- FullPage.js
- ECharts 5
- Font Awesome

## 数据库设计

- 14个核心表
- 符合第三范式
- 完整的外键关系
- 详细设计文档见 `plan/` 目录

## 开发文档

- [数据库设计文档](plan/)
- [用户角色设计](plan/06_user_roles_design.md)
- [API使用说明](README_api.md)
- [前端使用说明](frontend/README.md)

## 许可证

本项目为数据库课程作业项目。

