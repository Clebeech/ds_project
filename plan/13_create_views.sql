-- 创建数据库视图
-- 用于简化复杂查询，提高代码复用性

USE poverty_alleviation_832;

-- 1. 县域完整信息视图
-- 整合县域基础信息、贫困县状态、最新经济指标和农业数据
DROP VIEW IF EXISTS v_county_complete_info;
CREATE VIEW v_county_complete_info AS
SELECT 
    c.CountyCode,
    c.CountyName,
    c.Province,
    c.City,
    c.Longitude,
    c.Latitude,
    c.LandArea,
    pc.Region,
    pc.ExitYear,
    -- 最新年份的经济指标
    ce_latest.Year AS LatestEconYear,
    ce_latest.GDP,
    ce_latest.PerCapitaGDP,
    ce_latest.RuralDisposableIncome,
    ce_latest.FiscalRevenue,
    ce_latest.FiscalExpenditure,
    -- 最新年份的农业指标
    ca_latest.Year AS LatestAgriYear,
    ca_latest.AgriOutputValue,
    ca_latest.GrainOutput,
    -- 访谈统计
    COALESCE(interview_stats.interview_count, 0) AS InterviewCount,
    COALESCE(interview_stats.avg_quality, 0) AS AvgInterviewQuality
FROM county c
LEFT JOIN poverty_counties pc ON c.CountyCode = pc.CountyCode
-- 获取最新年份的经济数据
LEFT JOIN county_economy ce_latest ON c.CountyCode = ce_latest.CountyCode
    AND ce_latest.Year = (
        SELECT MAX(Year) 
        FROM county_economy 
        WHERE CountyCode = c.CountyCode
    )
-- 获取最新年份的农业数据
LEFT JOIN county_agriculture ca_latest ON c.CountyCode = ca_latest.CountyCode
    AND ca_latest.Year = (
        SELECT MAX(Year) 
        FROM county_agriculture 
        WHERE CountyCode = c.CountyCode
    )
-- 访谈统计
LEFT JOIN (
    SELECT 
        CountyCode,
        COUNT(*) AS interview_count,
        AVG(Quality) AS avg_quality
    FROM interviews
    GROUP BY CountyCode
) interview_stats ON c.CountyCode = interview_stats.CountyCode;

-- 2. 调研员工作统计视图
-- 整合调研员信息、负责县域、访谈统计
DROP VIEW IF EXISTS v_surveyor_work_statistics;
CREATE VIEW v_surveyor_work_statistics AS
SELECT 
    s.SurveyorID,
    s.Name,
    s.Department,
    s.Education,
    s.Major,
    s.TeamID,
    s.Role,
    s.Batch,
    s.CountyCode AS AssignedCountyCode,
    c.CountyName AS AssignedCountyName,
    c.Province AS AssignedProvince,
    -- 工作统计
    s.CompletedInterviews,
    s.PendingInterviews,
    COALESCE(interview_stats.total_interviews, 0) AS ActualInterviewCount,
    COALESCE(interview_stats.avg_quality, 0) AS AvgInterviewQuality,
    COALESCE(interview_stats.latest_interview_date, NULL) AS LatestInterviewDate,
    -- 访谈覆盖的县域数
    COALESCE(interview_stats.covered_counties, 0) AS CoveredCounties
FROM surveyors s
LEFT JOIN county c ON s.CountyCode = c.CountyCode
LEFT JOIN (
    SELECT 
        SurveyorID,
        COUNT(*) AS total_interviews,
        AVG(Quality) AS avg_quality,
        MAX(InterviewDate) AS latest_interview_date,
        COUNT(DISTINCT CountyCode) AS covered_counties
    FROM interviews
    GROUP BY SurveyorID
) interview_stats ON s.SurveyorID = interview_stats.SurveyorID;

-- 3. 贫困县汇总视图
-- 整合贫困县信息、摘帽状态、经济指标变化趋势
DROP VIEW IF EXISTS v_poverty_county_summary;
CREATE VIEW v_poverty_county_summary AS
SELECT 
    pc.CountyCode,
    pc.CountyName,
    pc.Province,
    pc.City,
    pc.Region,
    pc.ExitYear,
    -- 摘帽状态
    CASE 
        WHEN pc.ExitYear IS NOT NULL THEN '已摘帽'
        ELSE '未摘帽'
    END AS ExitStatus,
    -- 最新经济指标（摘帽年份或最新年份）
    COALESCE(ce_exit.GDP, ce_latest.GDP) AS LatestGDP,
    COALESCE(ce_exit.PerCapitaGDP, ce_latest.PerCapitaGDP) AS LatestPerCapitaGDP,
    COALESCE(ce_exit.RuralDisposableIncome, ce_latest.RuralDisposableIncome) AS LatestRuralIncome,
    -- GDP增长率（如果有多年数据）
    CASE 
        WHEN ce_old.GDP IS NOT NULL AND ce_old.GDP > 0 THEN
            ROUND(((COALESCE(ce_exit.GDP, ce_latest.GDP) - ce_old.GDP) / ce_old.GDP * 100), 2)
        ELSE NULL
    END AS GDPGrowthRate,
    -- 访谈统计
    COALESCE(interview_stats.interview_count, 0) AS InterviewCount
FROM poverty_counties pc
-- 摘帽年份的经济数据
LEFT JOIN county_economy ce_exit ON pc.CountyCode = ce_exit.CountyCode
    AND ce_exit.Year = pc.ExitYear
-- 最新年份的经济数据（如果没有摘帽年份数据）
LEFT JOIN county_economy ce_latest ON pc.CountyCode = ce_latest.CountyCode
    AND ce_latest.Year = (
        SELECT MAX(Year) 
        FROM county_economy 
        WHERE CountyCode = pc.CountyCode
    )
-- 最早年份的经济数据（用于计算增长率）
LEFT JOIN county_economy ce_old ON pc.CountyCode = ce_old.CountyCode
    AND ce_old.Year = (
        SELECT MIN(Year) 
        FROM county_economy 
        WHERE CountyCode = pc.CountyCode
    )
-- 访谈统计
LEFT JOIN (
    SELECT 
        CountyCode,
        COUNT(*) AS interview_count
    FROM interviews
    GROUP BY CountyCode
) interview_stats ON pc.CountyCode = interview_stats.CountyCode;

