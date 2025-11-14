"""
对比分析API
"""
from flask import Blueprint, jsonify, request
from backend.db import execute_query

bp = Blueprint('compare', __name__, url_prefix='/api/compare')


@bp.route('/economy', methods=['GET'])
def compare_economy():
    """对比多个县的经济数据"""
    county_codes = request.args.getlist('county_code')
    year = request.args.get('year', type=int)
    
    if not county_codes:
        return jsonify({'success': False, 'error': '请提供至少一个县代码'}), 400
    
    if len(county_codes) > 10:
        return jsonify({'success': False, 'error': '最多对比10个县'}), 400
    
    placeholders = ','.join(['%s'] * len(county_codes))
    sql = f"""
        SELECT c.CountyCode, c.CountyName, c.Province,
               e.Year, e.GDP, e.GDP_Primary, e.GDP_Secondary, e.GDP_Tertiary,
               e.PerCapitaGDP, e.RuralDisposableIncome,
               e.FiscalRevenue, e.FiscalExpenditure
        FROM county_economy e
        JOIN county c ON e.CountyCode = c.CountyCode
        WHERE e.CountyCode IN ({placeholders})
    """
    params = list(county_codes)
    
    if year:
        sql += " AND e.Year = %s"
        params.append(year)
    
    sql += " ORDER BY e.Year, e.GDP DESC"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/agriculture', methods=['GET'])
def compare_agriculture():
    """对比多个县的农业数据"""
    county_codes = request.args.getlist('county_code')
    year = request.args.get('year', type=int)
    
    if not county_codes:
        return jsonify({'success': False, 'error': '请提供至少一个县代码'}), 400
    
    if len(county_codes) > 10:
        return jsonify({'success': False, 'error': '最多对比10个县'}), 400
    
    placeholders = ','.join(['%s'] * len(county_codes))
    sql = f"""
        SELECT c.CountyCode, c.CountyName, c.Province,
               a.Year, a.CropArea, a.GrainOutput, a.MeatOutput,
               a.AgriOutputValue, a.RuralLaborForce
        FROM county_agriculture a
        JOIN county c ON a.CountyCode = c.CountyCode
        WHERE a.CountyCode IN ({placeholders})
    """
    params = list(county_codes)
    
    if year:
        sql += " AND a.Year = %s"
        params.append(year)
    
    sql += " ORDER BY a.Year, a.AgriOutputValue DESC"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/trend', methods=['GET'])
def compare_trend():
    """对比多个县的趋势数据"""
    county_codes = request.args.getlist('county_code')
    start_year = request.args.get('start_year', type=int, default=2000)
    end_year = request.args.get('end_year', type=int, default=2020)
    metric = request.args.get('metric', default='GDP')
    
    if not county_codes:
        return jsonify({'success': False, 'error': '请提供至少一个县代码'}), 400
    
    if len(county_codes) > 10:
        return jsonify({'success': False, 'error': '最多对比10个县'}), 400
    
    valid_metrics = ['GDP', 'PerCapitaGDP', 'RuralDisposableIncome', 'AgriOutputValue']
    if metric not in valid_metrics:
        return jsonify({'success': False, 'error': f'指标必须是: {", ".join(valid_metrics)}'}), 400
    
    placeholders = ','.join(['%s'] * len(county_codes))
    
    if metric == 'AgriOutputValue':
        table = 'county_agriculture'
    else:
        table = 'county_economy'
    
    sql = f"""
        SELECT c.CountyCode, c.CountyName, c.Province,
               t.Year, t.{metric}
        FROM {table} t
        JOIN county c ON t.CountyCode = c.CountyCode
        WHERE t.CountyCode IN ({placeholders})
          AND t.Year >= %s AND t.Year <= %s
    """
    params = list(county_codes) + [start_year, end_year]
    
    sql += " ORDER BY t.Year, c.CountyCode"
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result, 'count': len(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

