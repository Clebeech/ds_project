"""
县域数据API
"""
from flask import Blueprint, jsonify, request
from backend.db import execute_query

bp = Blueprint('counties', __name__, url_prefix='/api/counties')


@bp.route('', methods=['GET'])
def get_counties():
    """获取县列表"""
    region = request.args.get('region')
    exit_year = request.args.get('exit_year')
    province = request.args.get('province')
    
    sql = """
        SELECT c.CountyCode, c.CountyName, c.Province, c.City,
               c.Longitude, c.Latitude, p.ExitYear, p.Region
        FROM county c
        LEFT JOIN poverty_counties p ON c.CountyCode = p.CountyCode
        WHERE 1=1
    """
    params = []
    
    if region:
        sql += " AND p.Region = %s"
        params.append(region)
    if exit_year:
        sql += " AND p.ExitYear = %s"
        params.append(int(exit_year))
    if province:
        sql += " AND c.Province = %s"
        params.append(province)
    
    sql += " ORDER BY p.ExitYear, c.Province, c.CountyName"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
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

