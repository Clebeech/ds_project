-- 视图演示和测试查询
-- 用于验证视图的正确性和展示视图的用途

USE poverty_alleviation_832;

-- 1. 测试 v_county_complete_info 视图
-- 查看使用视图的查询效果
SELECT 
    CountyCode, CountyName, Province, Region, ExitYear,
    GDP, PerCapitaGDP, InterviewCount
FROM v_county_complete_info
WHERE ExitYear IS NOT NULL
ORDER BY GDP DESC
LIMIT 10;

-- 2. 测试 v_surveyor_work_statistics 视图
-- 查看调研员工作统计
SELECT 
    SurveyorID, Name, Role, TeamID,
    ActualInterviewCount, CoveredCounties, AvgInterviewQuality
FROM v_surveyor_work_statistics
ORDER BY ActualInterviewCount DESC
LIMIT 10;

-- 3. 测试 v_poverty_county_summary 视图
-- 查看贫困县汇总信息
SELECT 
    CountyCode, CountyName, Province, Region,
    ExitStatus, LatestGDP, GDPGrowthRate, InterviewCount
FROM v_poverty_county_summary
WHERE ExitYear IS NOT NULL
ORDER BY GDPGrowthRate DESC
LIMIT 10;

