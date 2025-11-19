-- 创建存储过程
-- 用于封装复杂业务逻辑，提高执行效率

USE poverty_alleviation_832;

-- 1. 县域综合报告存储过程
-- 生成县域完整报告，整合所有相关信息
DROP PROCEDURE IF EXISTS sp_get_county_comprehensive_report;
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
        ce_latest.FiscalRevenue, ce_latest.FiscalExpenditure,
        -- 经济指标（平均值）
        (SELECT AVG(GDP) FROM county_economy WHERE CountyCode = county_code) as AvgGDP,
        (SELECT AVG(PerCapitaGDP) FROM county_economy WHERE CountyCode = county_code) as AvgPerCapitaGDP,
        -- 农业指标（最新）
        ca_latest.Year as LatestAgriYear,
        ca_latest.AgriOutputValue, ca_latest.GrainOutput,
        -- 访谈统计
        COALESCE(interview_stats.interview_count, 0) as InterviewCount,
        COALESCE(interview_stats.avg_quality, 0) as AvgInterviewQuality,
        interview_stats.latest_interview_date as LatestInterviewDate,
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

-- 2. 地区统计分析存储过程
-- 按地区（西部地区/中部地区等）进行统计分析
DROP PROCEDURE IF EXISTS sp_statistics_by_region;
DELIMITER //
CREATE PROCEDURE sp_statistics_by_region(IN region_name VARCHAR(20))
BEGIN
    SELECT 
        region_name as Region,
        -- 县域统计
        COUNT(DISTINCT pc.CountyCode) as TotalCounties,
        COUNT(DISTINCT CASE WHEN pc.ExitYear IS NOT NULL THEN pc.CountyCode END) as ExitedCounties,
        COUNT(DISTINCT CASE WHEN pc.ExitYear IS NULL THEN pc.CountyCode END) as ActivePovertyCounties,
        -- 经济指标（平均值）
        AVG(ce.GDP) as AvgGDP,
        AVG(ce.PerCapitaGDP) as AvgPerCapitaGDP,
        AVG(ce.RuralDisposableIncome) as AvgRuralIncome,
        -- 农业指标（平均值）
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

-- 3. 调研员工作绩效存储过程
-- 获取调研员工作绩效分析
DROP PROCEDURE IF EXISTS sp_get_surveyor_performance;
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
        MAX(i.InterviewDate) as LatestInterviewDate,
        MIN(i.InterviewDate) as FirstInterviewDate
    FROM surveyors s
    LEFT JOIN county c ON s.CountyCode = c.CountyCode
    LEFT JOIN interviews i ON s.SurveyorID = i.SurveyorID
    WHERE s.SurveyorID = surveyor_id
    GROUP BY s.SurveyorID, s.Name, s.TeamID, s.Department, 
             s.CountyCode, c.CountyName, s.CompletedInterviews;
END //
DELIMITER ;

