"""
县域数据API
"""
import pymysql
from flask import Blueprint, jsonify, request
from backend.db import execute_query, get_db_connection

bp = Blueprint('counties', __name__, url_prefix='/api/counties')


@bp.route('', methods=['GET'])
def get_counties():
    """获取县列表，使用视图简化查询"""
    region = request.args.get('region')
    exit_year = request.args.get('exit_year')
    province = request.args.get('province')
    
    # 使用视图 v_county_complete_info 简化查询
    sql = """
        SELECT CountyCode, CountyName, Province, City,
               Longitude, Latitude, ExitYear, Region,
               GDP, PerCapitaGDP, RuralDisposableIncome,
               InterviewCount,
               -- 数据完整性评分：基于视图中的指标
               (
                   CASE WHEN GDP IS NOT NULL THEN 1 ELSE 0 END +
                   CASE WHEN AgriOutputValue IS NOT NULL THEN 1 ELSE 0 END +
                   CASE WHEN InterviewCount > 0 THEN 1 ELSE 0 END
               ) as DataCompleteness
        FROM v_county_complete_info
        WHERE 1=1
    """
    params = []
    
    if region:
        sql += " AND Region = %s"
        params.append(region)
    if exit_year:
        sql += " AND ExitYear = %s"
        params.append(int(exit_year))
    if province:
        sql += " AND Province = %s"
        params.append(province)
    
    sql += " ORDER BY DataCompleteness DESC, ExitYear, Province, CountyName"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result), 'note': 'Using view: v_county_complete_info'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<county_code>', methods=['GET'])
def get_county_detail(county_code):
    """获取县详情"""
    sql = """
        SELECT c.*, p.ExitYear, p.Region, n.TerrainRelief
        FROM county c
        LEFT JOIN poverty_counties p ON c.CountyCode = p.CountyCode
        LEFT JOIN county_nature n ON c.CountyCode = n.CountyCode
        WHERE c.CountyCode = %s
    """
    
    try:
        result = execute_query(sql, (county_code,))
        if result:
            return jsonify({'success': True, 'data': result[0]})
        else:
            return jsonify({'success': False, 'error': '县代码不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<county_code>/report', methods=['GET'])
def get_county_report(county_code):
    """获取县域综合报告（使用存储过程）"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 调用存储过程
        cursor.callproc('sp_get_county_comprehensive_report', (county_code,))
        result = cursor.fetchall()
        
        if result:
            return jsonify({
                'success': True, 
                'data': result[0] if len(result) == 1 else result,
                'note': 'Using stored procedure: sp_get_county_comprehensive_report'
            })
        else:
            return jsonify({'success': False, 'error': '县代码不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@bp.route('/<county_code>/economy', methods=['GET'])
def get_county_economy(county_code):
    """获取县经济数据"""
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    
    sql = """
        SELECT Year, GDP, GDP_Primary, GDP_Secondary, GDP_Tertiary,
               PerCapitaGDP, UrbanAvgWage, RuralDisposableIncome,
               FiscalRevenue, FiscalExpenditure, SavingsDeposit, LoanBalance,
               IndustrialOutput, IndustrialEnterpriseCount,
               FixedAssetInvestment, RetailSales
        FROM county_economy
        WHERE CountyCode = %s
    """
    params = [county_code]
    
    if start_year:
        sql += " AND Year >= %s"
        params.append(start_year)
    if end_year:
        sql += " AND Year <= %s"
        params.append(end_year)
    
    sql += " ORDER BY Year"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<county_code>/agriculture', methods=['GET'])
def get_county_agriculture(county_code):
    """获取县农业数据"""
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    
    sql = """
        SELECT Year, CropArea, MachineryPower, GrainOutput,
               CottonOutput, OilOutput, MeatOutput, AgriOutputValue,
               RuralLaborForce, AgriLaborForce
        FROM county_agriculture
        WHERE CountyCode = %s
    """
    params = [county_code]
    
    if start_year:
        sql += " AND Year >= %s"
        params.append(start_year)
    if end_year:
        sql += " AND Year <= %s"
        params.append(end_year)
    
    sql += " ORDER BY Year"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<county_code>/crops', methods=['GET'])
def get_county_crops(county_code):
    """获取县农作物种植面积"""
    year = request.args.get('year', type=int)
    
    sql = """
        SELECT Year, CropType, SownArea
        FROM crop_area
        WHERE CountyCode = %s
    """
    params = [county_code]
    
    if year:
        sql += " AND Year = %s"
        params.append(year)
    
    sql += " ORDER BY Year DESC, SownArea DESC"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<county_code>/population', methods=['GET'])
def get_county_population(county_code):
    """获取县人口数据"""
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)
    
    sql = """
        SELECT Year, RegisteredPopulation,
               PrimarySchoolTeachers, MiddleSchoolTeachers,
               PrimarySchoolStudents, MiddleSchoolStudents
        FROM county_population
        WHERE CountyCode = %s
    """
    params = [county_code]
    
    if start_year:
        sql += " AND Year >= %s"
        params.append(start_year)
    if end_year:
        sql += " AND Year <= %s"
        params.append(end_year)
    
    sql += " ORDER BY Year"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/map', methods=['GET'])
def get_counties_map():
    """获取地图可视化数据：经纬度、GDP、摘帽状态"""
    year = request.args.get('year', type=int)  # 可选：指定年份，默认使用最新年份
    
    # 如果没有指定年份，使用子查询获取每个县的最新GDP年份
    if year:
        sql = """
            SELECT 
                c.CountyCode,
                c.CountyName,
                c.Province,
                c.Longitude,
                c.Latitude,
                e.GDP,
                p.ExitYear,
                CASE WHEN p.ExitYear IS NOT NULL THEN 1 ELSE 0 END as IsExited
            FROM county c
            LEFT JOIN county_economy e ON c.CountyCode = e.CountyCode AND e.Year = %s
            LEFT JOIN poverty_counties p ON c.CountyCode = p.CountyCode
            WHERE c.Longitude IS NOT NULL 
              AND c.Latitude IS NOT NULL
              AND c.Longitude != 0 
              AND c.Latitude != 0
        """
        params = [year]
    else:
        # 获取每个县最新年份的GDP
        sql = """
            SELECT 
                c.CountyCode,
                c.CountyName,
                c.Province,
                c.Longitude,
                c.Latitude,
                latest_economy.GDP,
                p.ExitYear,
                CASE WHEN p.ExitYear IS NOT NULL THEN 1 ELSE 0 END as IsExited
            FROM county c
            LEFT JOIN (
                SELECT e1.CountyCode, e1.GDP, e1.Year
                FROM county_economy e1
                INNER JOIN (
                    SELECT CountyCode, MAX(Year) as MaxYear
                    FROM county_economy
                    GROUP BY CountyCode
                ) e2 ON e1.CountyCode = e2.CountyCode AND e1.Year = e2.MaxYear
            ) latest_economy ON c.CountyCode = latest_economy.CountyCode
            LEFT JOIN poverty_counties p ON c.CountyCode = p.CountyCode
            WHERE c.Longitude IS NOT NULL 
              AND c.Latitude IS NOT NULL
              AND c.Longitude != 0 
              AND c.Latitude != 0
        """
        params = []
    
    sql += " ORDER BY c.Province, c.CountyName"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

