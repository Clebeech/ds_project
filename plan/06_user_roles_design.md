# 用户角色和功能设计

## 服务目标

为政府扶贫政策分析师提供脱贫案例库支持，通过整合县域访谈信息、宏观经济、农业结构、自然地理等数据，支持政策分析和决策。

## 用户角色

### 1. 政府扶贫政策分析师（主要用户）
**角色描述**：负责分析脱贫案例，制定和评估扶贫政策

**核心功能**：
- 查询贫困县基本信息（摘帽时间、地理位置等）
- 分析县域经济发展趋势（GDP、收入、产业结构变化）
- 查看农业数据（农作物种植、农业产出结构）
- 检索访谈记录（按县、按主题、按时间）
- 对比不同县的脱贫路径和成效
- 生成脱贫案例报告

**SQL操作对应**：
- `SELECT` - 查询县域数据、访谈记录
- `JOIN` - 关联多表数据（县+经济+农业+访谈）
- `GROUP BY` - 按地区、时间分组统计
- `ORDER BY` - 按摘帽时间、GDP等排序
- `WHERE` - 筛选条件（贫困县、年份范围等）
- `COUNT`, `SUM`, `AVG` - 统计分析

### 2. 调研管理员（次要用户）
**角色描述**：管理调研员和访谈记录

**核心功能**：
- 查看调研员信息（所属分队、负责县域）
- 管理访谈记录（查看、筛选、统计）
- 分析访谈质量（按调研员、按县统计）

**SQL操作对应**：
- `SELECT` - 查询调研员、访谈记录
- `JOIN` - 关联调研员和访谈表
- `GROUP BY` - 按调研员、县分组统计
- `UPDATE` - 更新访谈记录（如果需要）

## 功能模块设计

### 模块1：县域概览
**功能**：展示832个贫困县的基本信息
- 贫困县列表（按摘帽时间、地区分类）
- 县域地图（地理分布）
- 基础统计（总数、已摘帽数、按地区分布）

**SQL示例**：
```sql
-- 查询所有贫困县及摘帽时间
SELECT c.CountyCode, c.CountyName, c.Province, c.City, 
       p.ExitYear, p.Region
FROM county c
LEFT JOIN poverty_counties p ON c.CountyCode = p.CountyCode
WHERE p.CountyCode IS NOT NULL
ORDER BY p.ExitYear, c.Province;
```

### 模块2：经济数据分析
**功能**：分析县域经济发展趋势
- GDP趋势图（多年数据对比）
- 产业结构分析（一二三产业占比）
- 收入水平分析（城镇/农村人均收入）
- 财政收支分析

**SQL示例**：
```sql
-- 查询某县多年GDP数据
SELECT Year, GDP, GDP_Primary, GDP_Secondary, GDP_Tertiary,
       PerCapitaGDP, RuralDisposableIncome
FROM county_economy
WHERE CountyCode = '130125'
ORDER BY Year;
```

### 模块3：农业数据分析
**功能**：分析县域农业结构
- 主要农作物种植面积
- 农业产出结构（粮食、经济作物、畜牧业）
- 农业产值趋势

**SQL示例**：
```sql
-- 查询某县主要农作物种植面积
SELECT Year, CropType, SUM(SownArea) as TotalArea
FROM crop_area
WHERE CountyCode = '130125'
GROUP BY Year, CropType
ORDER BY Year DESC, TotalArea DESC;
```

### 模块4：访谈记录检索
**功能**：检索和分析访谈内容
- 按县检索访谈
- 按调研员检索访谈
- 按关键词搜索访谈内容
- 访谈质量统计

**SQL示例**：
```sql
-- 查询某县所有访谈记录
SELECT i.InterviewID, i.InterviewDate, i.IntervieweeName,
       i.IntervieweeInfo, i.Quality, s.Name as SurveyorName
FROM interviews i
JOIN surveyors s ON i.SurveyorID = s.SurveyorID
WHERE i.CountyCode = '130125'
ORDER BY i.InterviewDate DESC;
```

### 模块5：对比分析
**功能**：对比不同县的脱贫路径
- 选择多个县进行对比
- 对比经济指标
- 对比农业结构
- 对比访谈主题

**SQL示例**：
```sql
-- 对比多个县的GDP数据
SELECT c.CountyName, e.Year, e.GDP, e.PerCapitaGDP
FROM county_economy e
JOIN county c ON e.CountyCode = c.CountyCode
WHERE e.CountyCode IN ('130125', '410526', '150928')
  AND e.Year = 2020
ORDER BY e.GDP DESC;
```

### 模块6：数据可视化
**功能**：图表展示数据
- 地图可视化（县域分布）
- 折线图（趋势分析）
- 柱状图（对比分析）
- 饼图（结构分析）

## 页面结构设计

### 首页（Hero页面）
- 超大数字：832个贫困县
- 核心数据概览
- 进入系统按钮

### 县域概览页
- 贫困县列表
- 地图可视化
- 筛选功能（按地区、摘帽时间）

### 县域详情页
- 基本信息
- 经济数据图表
- 农业数据图表
- 访谈记录列表

### 访谈检索页
- 搜索框
- 筛选条件
- 访谈列表
- 访谈详情

### 对比分析页
- 县选择器
- 对比图表
- 数据表格

## 技术实现对应

### 后端API端点设计
- `GET /api/counties` - 获取县列表
- `GET /api/counties/:code` - 获取县详情
- `GET /api/counties/:code/economy` - 获取经济数据
- `GET /api/counties/:code/agriculture` - 获取农业数据
- `GET /api/interviews` - 获取访谈列表
- `GET /api/interviews/:id` - 获取访谈详情
- `GET /api/compare` - 对比分析

### 前端页面路由
- `/` - 首页
- `/counties` - 县域概览
- `/counties/:code` - 县域详情
- `/interviews` - 访谈检索
- `/compare` - 对比分析

