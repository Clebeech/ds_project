"""
统计数据API
"""
import pymysql
from flask import Blueprint, jsonify, request
from backend.db import execute_query, get_db_connection

bp = Blueprint('stats', __name__, url_prefix='/api/stats')


@bp.route('/overview', methods=['GET'])
def get_overview():
    """获取系统概览统计"""
    try:
        stats = {}
        
        # 贫困县总数
        result = execute_query("SELECT COUNT(*) as total FROM poverty_counties")
        stats['poverty_counties'] = result[0]['total'] if result else 0
        
        # 已摘帽县数
        result = execute_query("SELECT COUNT(*) as total FROM poverty_counties WHERE ExitYear IS NOT NULL")
        stats['exited_counties'] = result[0]['total'] if result else 0
        
        # 访谈记录总数
        result = execute_query("SELECT COUNT(*) as total FROM interviews")
        stats['interviews'] = result[0]['total'] if result else 0
        
        # 调研员总数
        result = execute_query("SELECT COUNT(*) as total FROM surveyors")
        stats['surveyors'] = result[0]['total'] if result else 0
        
        # 按地区分布
        result = execute_query("""
            SELECT Region, COUNT(*) as count
            FROM poverty_counties
            GROUP BY Region
        """)
        stats['by_region'] = result if result else []
        
        # 按摘帽年份分布
        result = execute_query("""
            SELECT ExitYear, COUNT(*) as count
            FROM poverty_counties
            WHERE ExitYear IS NOT NULL
            GROUP BY ExitYear
            ORDER BY ExitYear
        """)
        stats['by_exit_year'] = result if result else []
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/region', methods=['GET'])
def get_region_statistics():
    """按地区统计分析（使用存储过程）"""
    region = request.args.get('region')
    if not region:
        return jsonify({'success': False, 'error': '缺少region参数'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 调用存储过程
        cursor.callproc('sp_statistics_by_region', (region,))
        result = cursor.fetchall()
        
        if result:
            return jsonify({
                'success': True,
                'data': result[0] if len(result) == 1 else result,
                'note': 'Using stored procedure: sp_statistics_by_region'
            })
        else:
            return jsonify({'success': False, 'error': '该地区无数据'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@bp.route('/complex/above-average', methods=['GET'])
def get_above_average_surveyors():
    """使用HAVING子句：找出访谈次数超过平均值的调研员"""
    sql = """
        SELECT 
            s.SurveyorID,
            s.Name,
            s.TeamID,
            COUNT(i.InterviewID) as InterviewCount,
            AVG(i.Quality) as AvgQuality
        FROM surveyors s
        LEFT JOIN interviews i ON s.SurveyorID = i.SurveyorID
        GROUP BY s.SurveyorID, s.Name, s.TeamID
        HAVING InterviewCount > (
            SELECT AVG(cnt) 
            FROM (
                SELECT COUNT(*) as cnt
                FROM interviews
                GROUP BY SurveyorID
            ) sub
        )
        ORDER BY InterviewCount DESC
    """
    
    try:
        result = execute_query(sql)
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result) if result else 0,
            'note': 'Using HAVING clause to filter by aggregate function'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/complex/top-gdp-growth', methods=['GET'])
def get_top_gdp_growth():
    """使用窗口函数和子查询：找出摘帽后GDP增长最快的10个县"""
    sql = """
        SELECT 
            pc.CountyCode,
            c.CountyName,
            pc.Province,
            pc.ExitYear,
            latest.GDP as LatestGDP,
            earliest.GDP as EarliestGDP,
            CASE 
                WHEN earliest.GDP > 0 
                THEN ((latest.GDP - earliest.GDP) / earliest.GDP * 100)
                ELSE 0
            END as GDPGrowthRate
        FROM poverty_counties pc
        LEFT JOIN county c ON pc.CountyCode = c.CountyCode
        LEFT JOIN (
            SELECT CountyCode, GDP
            FROM county_economy ce1
            WHERE ce1.Year = (
                SELECT MAX(Year) 
                FROM county_economy 
                WHERE CountyCode = ce1.CountyCode
            )
        ) latest ON pc.CountyCode = latest.CountyCode
        LEFT JOIN (
            SELECT CountyCode, GDP
            FROM county_economy ce2
            WHERE ce2.Year = (
                SELECT MIN(Year) 
                FROM county_economy 
                WHERE CountyCode = ce2.CountyCode
                    AND Year >= (SELECT ExitYear FROM poverty_counties WHERE CountyCode = ce2.CountyCode)
            )
        ) earliest ON pc.CountyCode = earliest.CountyCode
        WHERE pc.ExitYear IS NOT NULL
            AND latest.GDP IS NOT NULL
            AND earliest.GDP IS NOT NULL
            AND earliest.GDP > 0
        ORDER BY GDPGrowthRate DESC
        LIMIT 10
    """
    
    try:
        result = execute_query(sql)
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result) if result else 0,
            'note': 'Using subqueries to calculate GDP growth rate'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

