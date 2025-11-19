from flask import Blueprint, jsonify, request, session
from backend.db import execute_query

bp = Blueprint('surveyors', __name__, url_prefix='/api/surveyors')

@bp.route('', methods=['GET'])
def get_surveyors():
    """获取调研员列表"""
    keyword = request.args.get('keyword')
    county_code = request.args.get('county_code')
    limit = request.args.get('limit', type=int, default=50)
    offset = request.args.get('offset', type=int, default=0)

    # 基础查询 - 关联 county 表获取县名
    sql = """
        SELECT s.SurveyorID, s.Name, s.Gender, s.Department, s.Education, s.Major,
               s.TeamID, s.Role, s.CompletedInterviews, s.Expertise,
               s.CountyCode, c.CountyName, c.Province,
               -- 敏感字段仅对特定角色可见，这里先查出来，后续在Python中过滤
               s.Phone, s.Email
        FROM surveyors s
        LEFT JOIN county c ON s.CountyCode = c.CountyCode
        WHERE 1=1
    """
    params = []

    if keyword:
        sql += " AND (s.Name LIKE %s OR s.SurveyorID LIKE %s)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    if county_code:
        sql += " AND s.CountyCode = %s"
        params.append(county_code)

    sql += " ORDER BY s.CompletedInterviews DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        result = execute_query(sql, params)
        
        # 隐私保护：仅管理员、分析师、调研员可见联系方式
        user_role = session.get('role')
        is_privileged = user_role in ['admin', 'analyst', 'surveyor']
        
        for row in result:
            if not is_privileged:
                row.pop('Phone', None)
                row.pop('Email', None)
        
        # 获取总数
        count_sql = "SELECT COUNT(*) as total FROM surveyors s WHERE 1=1"
        count_params = []
        
        if keyword:
            count_sql += " AND (s.Name LIKE %s OR s.SurveyorID LIKE %s)"
            count_params.extend([f'%{keyword}%', f'%{keyword}%'])
        if county_code:
            count_sql += " AND s.CountyCode = %s"
            count_params.append(county_code)
            
        total_res = execute_query(count_sql, count_params)
        total = total_res[0]['total'] if total_res else 0

        return jsonify({
            'success': True,
            'data': result,
            'total': total
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_surveyor_stats():
    """获取调研团队统计信息"""
    sql = """
        SELECT 
            COUNT(*) as total_surveyors,
            SUM(CompletedInterviews) as total_interviews,
            COUNT(DISTINCT CountyCode) as covered_counties,
            COUNT(DISTINCT TeamID) as total_teams
        FROM surveyors
    """
    try:
        result = execute_query(sql)
        return jsonify({'success': True, 'data': result[0] if result else {}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

