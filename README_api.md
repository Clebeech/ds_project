# 后端API使用说明

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置数据库

编辑 `backend/db.py` 文件，修改数据库连接配置：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'poverty_alleviation_832',
    'charset': 'utf8mb4'
}
```

## 运行API服务

```bash
# 方式1：使用启动脚本（推荐）
python run.py

# 方式2：直接运行
python -m backend.app

# 方式3：使用Flask CLI
export FLASK_APP=backend.app
flask run
```

API服务将在 `http://localhost:5001` 启动

**访问链接：**
- 后端API: http://localhost:5001/api
- 前端应用: http://localhost:8000

## API端点

### 1. 县域数据 API (`/api/counties`)

#### 获取县列表
```
GET /api/counties
参数:
  - region: 所属地域（可选）
  - exit_year: 摘帽时间（可选）
  - province: 所属省份（可选）
```

#### 获取县详情
```
GET /api/counties/<county_code>
```

#### 获取县经济数据
```
GET /api/counties/<county_code>/economy
参数:
  - start_year: 起始年份（可选）
  - end_year: 结束年份（可选）
```

#### 获取县农业数据
```
GET /api/counties/<county_code>/agriculture
参数:
  - start_year: 起始年份（可选）
  - end_year: 结束年份（可选）
```

#### 获取县农作物数据
```
GET /api/counties/<county_code>/crops
参数:
  - year: 年份（可选）
```

#### 获取县人口数据
```
GET /api/counties/<county_code>/population
参数:
  - start_year: 起始年份（可选）
  - end_year: 结束年份（可选）
```

### 2. 访谈记录 API (`/api/interviews`)

#### 获取访谈列表
```
GET /api/interviews
参数:
  - county_code: 县代码（可选）
  - surveyor_id: 调研员ID（可选）
  - keyword: 关键词搜索（可选）
  - limit: 每页数量（默认50）
  - offset: 偏移量（默认0）
```

#### 获取访谈详情
```
GET /api/interviews/<interview_id>
```

#### 获取访谈统计
```
GET /api/interviews/stats
参数:
  - county_code: 县代码（可选）
```

### 3. 对比分析 API (`/api/compare`)

#### 对比经济数据
```
GET /api/compare/economy
参数:
  - county_code: 县代码（可多个，最多10个）
  - year: 年份（可选）
```

#### 对比农业数据
```
GET /api/compare/agriculture
参数:
  - county_code: 县代码（可多个，最多10个）
  - year: 年份（可选）
```

#### 对比趋势数据
```
GET /api/compare/trend
参数:
  - county_code: 县代码（可多个，最多10个）
  - start_year: 起始年份（默认2000）
  - end_year: 结束年份（默认2020）
  - metric: 指标（GDP/PerCapitaGDP/RuralDisposableIncome/AgriOutputValue）
```

### 4. 统计数据 API (`/api/stats`)

#### 获取系统概览
```
GET /api/stats/overview
```

## 响应格式

所有API返回JSON格式：

```json
{
  "success": true,
  "data": [...],
  "count": 10
}
```

错误响应：

```json
{
  "success": false,
  "error": "错误信息"
}
```

## 示例请求

### 使用curl命令

```bash
# 获取所有贫困县
curl http://localhost:5001/api/counties

# 获取某县经济数据
curl http://localhost:5001/api/counties/130125/economy?start_year=2010&end_year=2020

# 获取访谈列表
curl http://localhost:5001/api/interviews?county_code=130125&limit=10

# 对比多个县的经济数据
curl "http://localhost:5001/api/compare/economy?county_code=130125&county_code=410526&year=2020"
```

### 直接在浏览器中访问

- [获取所有贫困县](http://localhost:5001/api/counties)
- [获取系统概览统计](http://localhost:5001/api/stats/overview)
- [获取访谈统计](http://localhost:5001/api/interviews/stats)