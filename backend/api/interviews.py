"""
访谈记录API
"""
from flask import Blueprint, jsonify, request, session
from backend.db import execute_query
from backend.api.auth import login_required

bp = Blueprint('interviews', __name__, url_prefix='/api/interviews')


@bp.route('', methods=['GET'])
def get_interviews():
    """获取访谈列表"""
    county_code = request.args.get('county_code')
    surveyor_id = request.args.get('surveyor_id')
    keyword = request.args.get('keyword')
    limit = request.args.get('limit', type=int, default=50)
    offset = request.args.get('offset', type=int, default=0)
    
    sql = """
        SELECT i.InterviewID, i.InterviewDate, i.IntervieweeName,
               i.IntervieweeInfo, i.Content, i.InterviewLocation, i.Quality,
               i.CountyCode, c.CountyName, s.Name as SurveyorName, s.SurveyorID
        FROM interviews i
        JOIN county c ON i.CountyCode = c.CountyCode
        LEFT JOIN surveyors s ON i.SurveyorID = s.SurveyorID
        WHERE 1=1
    """
    params = []
    
    if county_code:
        sql += " AND i.CountyCode = %s"
        params.append(county_code)
    if surveyor_id:
        sql += " AND i.SurveyorID = %s"
        params.append(surveyor_id)
    if keyword:
        sql += " AND (i.Content LIKE %s OR i.IntervieweeName LIKE %s)"
        keyword_pattern = f'%{keyword}%'
        params.extend([keyword_pattern, keyword_pattern])
    
    sql += " ORDER BY i.InterviewDate DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    try:
        result = execute_query(sql, params)
        
        # 如果未登录，隐藏访谈内容详情
        if 'user_id' not in session:
            for row in result:
                row['Content'] = "请登录分析师账号查看详细访谈内容"
                # 也可以截取前几个字: row['Content'] = (row['Content'] or '')[:50] + '...'
        
        # 获取总数
        count_sql = """
            SELECT COUNT(*) as total
            FROM interviews i
            WHERE 1=1
        """
        count_params = []
        if county_code:
            count_sql += " AND i.CountyCode = %s"
            count_params.append(county_code)
        if surveyor_id:
            count_sql += " AND i.SurveyorID = %s"
            count_params.append(surveyor_id)
        if keyword:
            count_sql += " AND (i.Content LIKE %s OR i.IntervieweeName LIKE %s)"
            keyword_pattern = f'%{keyword}%'
            count_params.extend([keyword_pattern, keyword_pattern])
        
        total_result = execute_query(count_sql, count_params)
        total = total_result[0]['total'] if total_result else 0
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result),
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<interview_id>', methods=['GET'])
@login_required
def get_interview_detail(interview_id):
    """获取访谈详情"""
    sql = """
        SELECT i.*, c.CountyName, c.Province, c.City,
               s.Name as SurveyorName, s.Department, s.TeamID
        FROM interviews i
        JOIN county c ON i.CountyCode = c.CountyCode
        LEFT JOIN surveyors s ON i.SurveyorID = s.SurveyorID
        WHERE i.InterviewID = %s
    """
    
    try:
        result = execute_query(sql, (interview_id,))
        if result:
            return jsonify({'success': True, 'data': result[0]})
        else:
            return jsonify({'success': False, 'error': '访谈记录不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_interview_stats():
    """获取访谈统计"""
    county_code = request.args.get('county_code')
    
    sql = """
        SELECT 
            COUNT(*) as total,
            AVG(Quality) as avg_quality,
            COUNT(DISTINCT CountyCode) as county_count,
            COUNT(DISTINCT SurveyorID) as surveyor_count
        FROM interviews
    """
    params = []
    
    if county_code:
        sql += " WHERE CountyCode = %s"
        params.append(county_code)
    
    try:
        result = execute_query(sql, params)
        return jsonify({'success': True, 'data': result[0] if result else {}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

