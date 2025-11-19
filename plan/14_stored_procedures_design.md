# 存储过程设计计划

## 目标
创建1-2个存储过程，封装复杂业务逻辑，体现数据库系统的能力。

## 设计的存储过程

### 1. `sp_get_county_comprehensive_report(IN county_code CHAR(6))`
**功能**：生成县域综合报告，整合所有相关信息

**返回数据**：
- 县域基本信息（名称、省市、位置）
- 贫困县状态（是否贫困县、摘帽年份、区域）
- 经济指标（最新GDP、人均GDP、历年平均值）
- 农业指标（最新农业产值、粮食产量）
- 访谈统计（访谈次数、平均质量、最新访谈日期）
- 调研员信息（负责的调研员、团队）

**使用场景**：
- `/api/counties/<code>/report` - 获取县域完整报告
- 前端"县域详情"页面展示
- 数据导出功能

**SQL逻辑**：
```sql
DELIMITER //
CREATE PROCEDURE sp_get_county_comprehensive_report(IN county_code CHAR(6))
BEGIN
    SELECT 
        -- 基础信息
        c.CountyCode, c.CountyName, c.Province, c.City,
        c.Longitude, c.Latitude, c.LandArea,
        -- 贫困县信息
        pc.ExitYear, pc.Region,
        CASE WHEN pc.CountyCode IS NOT NULL THEN '是' ELSE '否' END as IsPovertyCounty,
        -- 经济指标（最新）
        ce_latest.Year as LatestEconYear,
        ce_latest.GDP, ce_latest.PerCapitaGDP,
        ce_latest.RuralDisposableIncome,
        -- 经济指标（平均值）
        (SELECT AVG(GDP) FROM county_economy WHERE CountyCode = county_code) as AvgGDP,
        (SELECT AVG(PerCapitaGDP) FROM county_economy WHERE CountyCode = county_code) as AvgPerCapitaGDP,
        -- 农业指标（最新）
        ca_latest.Year as LatestAgriYear,
        ca_latest.AgriOutputValue, ca_latest.GrainOutput,
        -- 访谈统计
        interview_stats.interview_count,
        interview_stats.avg_quality,
        interview_stats.latest_interview_date,
        -- 调研员信息
        s.SurveyorID, s.Name as SurveyorName, s.TeamID
    FROM county c
    LEFT JOIN poverty_counties pc ON c.CountyCode = pc.CountyCode
    LEFT JOIN county_economy ce_latest ON c.CountyCode = ce_latest.CountyCode
        AND ce_latest.Year = (SELECT MAX(Year) FROM county_economy WHERE CountyCode = county_code)
    LEFT JOIN county_agriculture ca_latest ON c.CountyCode = ca_latest.CountyCode
        AND ca_latest.Year = (SELECT MAX(Year) FROM county_agriculture WHERE CountyCode = county_code)
    LEFT JOIN (
        SELECT 
            CountyCode,
            COUNT(*) as interview_count,
            AVG(Quality) as avg_quality,
            MAX(InterviewDate) as latest_interview_date
        FROM interviews
        WHERE CountyCode = county_code
        GROUP BY CountyCode
    ) interview_stats ON c.CountyCode = interview_stats.CountyCode
    LEFT JOIN surveyors s ON c.CountyCode = s.CountyCode
    WHERE c.CountyCode = county_code;
END //
DELIMITER ;
```

---

### 2. `sp_statistics_by_region(IN region_name VARCHAR(20))`
**功能**：按地区（西部地区/中部地区等）进行统计分析

**返回数据**：
- 县域数量统计
- 经济指标汇总（平均GDP、平均人均GDP）
- 摘帽情况（已摘帽数量、未摘帽数量）
- 访谈统计（总访谈次数、平均质量）
- 调研覆盖情况

**使用场景**：
- `/api/stats/region?region=西部地区` - 地区统计分析
- 前端"数据概览"页面
- 数据对比分析

**SQL逻辑**：
```sql
DELIMITER //
CREATE PROCEDURE sp_statistics_by_region(IN region_name VARCHAR(20))
BEGIN
    SELECT 
        region_name as Region,
        -- 县域统计
        COUNT(DISTINCT pc.CountyCode) as TotalCounties,
        COUNT(DISTINCT CASE WHEN pc.ExitYear IS NOT NULL THEN pc.CountyCode END) as ExitedCounties,
        COUNT(DISTINCT CASE WHEN pc.ExitYear IS NULL THEN pc.CountyCode END) as ActivePovertyCounties,
        -- 经济指标
        AVG(ce.GDP) as AvgGDP,
        AVG(ce.PerCapitaGDP) as AvgPerCapitaGDP,
        AVG(ce.RuralDisposableIncome) as AvgRuralIncome,
        -- 农业指标
        AVG(ca.AgriOutputValue) as AvgAgriOutput,
        -- 访谈统计
        COUNT(DISTINCT i.InterviewID) as TotalInterviews,
        AVG(i.Quality) as AvgInterviewQuality,
        COUNT(DISTINCT i.SurveyorID) as ActiveSurveyors,
        COUNT(DISTINCT i.CountyCode) as CoveredCounties
    FROM poverty_counties pc
    LEFT JOIN county_economy ce ON pc.CountyCode = ce.CountyCode
        AND ce.Year = (SELECT MAX(Year) FROM county_economy WHERE CountyCode = pc.CountyCode)
    LEFT JOIN county_agriculture ca ON pc.CountyCode = ca.CountyCode
        AND ca.Year = (SELECT MAX(Year) FROM county_agriculture WHERE CountyCode = pc.CountyCode)
    LEFT JOIN interviews i ON pc.CountyCode = i.CountyCode
    WHERE pc.Region = region_name;
END //
DELIMITER ;
```

---

### 3. `sp_get_surveyor_performance(IN surveyor_id VARCHAR(20))`
**功能**：获取调研员工作绩效分析

**返回数据**：
- 基本信息（姓名、团队、负责县域）
- 访谈统计（总次数、平均质量、完成率）
- 覆盖范围（负责县域、实际覆盖县域）
- 时间趋势（每月访谈数量）
- 工作质量评级

**使用场景**：
- `/api/surveyors/<id>/performance` - 调研员绩效报告
- 管理员评估调研员工作
- 数据可视化展示

**SQL逻辑**：
```sql
DELIMITER //
CREATE PROCEDURE sp_get_surveyor_performance(IN surveyor_id VARCHAR(20))
BEGIN
    SELECT 
        s.SurveyorID, s.Name, s.TeamID, s.Department,
        s.CountyCode, c.CountyName,
        -- 访谈统计
        COUNT(i.InterviewID) as TotalInterviews,
        AVG(i.Quality) as AvgQuality,
        s.CompletedInterviews as AssignedInterviews,
        CASE 
            WHEN s.CompletedInterviews > 0 
            THEN (COUNT(i.InterviewID) * 100.0 / s.CompletedInterviews)
            ELSE 0 
        END as CompletionRate,
        -- 覆盖范围
        COUNT(DISTINCT i.CountyCode) as CoveredCounties,
        -- 时间趋势（最近6个月）
        DATE_FORMAT(i.InterviewDate, '%Y-%m') as Month,
        COUNT(*) as MonthlyInterviews
    FROM surveyors s
    LEFT JOIN county c ON s.CountyCode = c.CountyCode
    LEFT JOIN interviews i ON s.SurveyorID = i.SurveyorID
    WHERE s.SurveyorID = surveyor_id
    GROUP BY s.SurveyorID, s.Name, s.TeamID, s.Department, 
             s.CountyCode, c.CountyName, s.CompletedInterviews,
             DATE_FORMAT(i.InterviewDate, '%Y-%m')
    ORDER BY Month DESC;
END //
DELIMITER ;
```

---

## 实施步骤

1. **创建SQL文件**：`plan/14_create_procedures.sql`
2. **创建初始化脚本**：`backend/init_procedures.py`
3. **创建API接口**：在对应的blueprint中添加存储过程调用
4. **测试验证**：创建测试脚本验证存储过程功能

## API接口设计

### 1. 县域综合报告
```
GET /api/counties/<county_code>/report
```
调用 `sp_get_county_comprehensive_report`

### 2. 地区统计
```
GET /api/stats/region?region=西部地区
```
调用 `sp_statistics_by_region`

### 3. 调研员绩效
```
GET /api/surveyors/<surveyor_id>/performance
```
调用 `sp_get_surveyor_performance`

