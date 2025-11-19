"""
视图演示API - 展示视图的使用效果
"""
from flask import Blueprint, jsonify, request
from backend.db import execute_query

bp = Blueprint('views_demo', __name__, url_prefix='/api/views')

@bp.route('/county-complete', methods=['GET'])
def get_county_complete():
    """使用视图 v_county_complete_info 获取县域完整信息"""
    limit = request.args.get('limit', type=int, default=10)
    region = request.args.get('region')
    
    sql = """
        SELECT CountyCode, CountyName, Province, Region, ExitYear,
               LatestEconYear, GDP, PerCapitaGDP, RuralDisposableIncome,
               LatestAgriYear, AgriOutputValue,
               InterviewCount, AvgInterviewQuality
        FROM v_county_complete_info
        WHERE 1=1
    """
    params = []
    
    if region:
        sql += " AND Region = %s"
        params.append(region)
    
    sql += " ORDER BY GDP DESC LIMIT %s"
    params.append(limit)
    
    try:
        result = execute_query(sql, params)
        return jsonify({
            'success': True, 
            'data': result,
            'view_name': 'v_county_complete_info',
            'description': '整合县域基础信息、贫困县状态、最新经济指标和农业数据'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/surveyor-stats', methods=['GET'])
def get_surveyor_stats():
    """使用视图 v_surveyor_work_statistics 获取调研员工作统计"""
    limit = request.args.get('limit', type=int, default=10)
    team_id = request.args.get('team_id')
    
    sql = """
        SELECT SurveyorID, Name, Department, Role, TeamID,
               AssignedCountyName, AssignedProvince,
               CompletedInterviews, ActualInterviewCount,
               CoveredCounties, AvgInterviewQuality, LatestInterviewDate
        FROM v_surveyor_work_statistics
        WHERE 1=1
    """
    params = []
    
    if team_id:
        sql += " AND TeamID = %s"
        params.append(team_id)
    
    sql += " ORDER BY ActualInterviewCount DESC LIMIT %s"
    params.append(limit)
    
    try:
        result = execute_query(sql, params)
        return jsonify({
            'success': True,
            'data': result,
            'view_name': 'v_surveyor_work_statistics',
            'description': '整合调研员信息、负责县域、访谈统计'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/poverty-summary', methods=['GET'])
def get_poverty_summary():
    """使用视图 v_poverty_county_summary 获取贫困县汇总"""
    limit = request.args.get('limit', type=int, default=10)
    region = request.args.get('region')
    exit_status = request.args.get('exit_status')  # '已摘帽' or '未摘帽'
    
    sql = """
        SELECT CountyCode, CountyName, Province, Region,
               ExitYear, ExitStatus,
               LatestGDP, LatestPerCapitaGDP, LatestRuralIncome,
               GDPGrowthRate, InterviewCount
        FROM v_poverty_county_summary
        WHERE 1=1
    """
    params = []
    
    if region:
        sql += " AND Region = %s"
        params.append(region)
    if exit_status:
        sql += " AND ExitStatus = %s"
        params.append(exit_status)
    
    sql += " ORDER BY GDPGrowthRate DESC LIMIT %s"
    params.append(limit)
    
    try:
        result = execute_query(sql, params)
        return jsonify({
            'success': True,
            'data': result,
            'view_name': 'v_poverty_county_summary',
            'description': '整合贫困县信息、摘帽状态、经济指标变化趋势'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_views():
    """列出所有已创建的视图"""
    sql = """
        SELECT TABLE_NAME as view_name, 
               VIEW_DEFINITION as definition
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = 'poverty_alleviation_832'
    """
    try:
        result = execute_query(sql)
        return jsonify({
            'success': True,
            'views': result,
            'count': len(result)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

