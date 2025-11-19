import pymysql
from flask import Blueprint, jsonify, request, session
from backend.db import execute_query, get_db_connection

bp = Blueprint('surveyors', __name__, url_prefix='/api/surveyors')

@bp.route('', methods=['GET'])
def get_surveyors():
    """获取调研员列表 - 使用视图简化查询"""
    keyword = request.args.get('keyword')
    county_code = request.args.get('county_code')
    limit = request.args.get('limit', type=int, default=50)
    offset = request.args.get('offset', type=int, default=0)

    # 使用视图 v_surveyor_work_statistics 简化查询，但需要额外JOIN获取Expertise等字段
    sql = """
        SELECT v.SurveyorID, v.Name, v.Department, v.Education, v.Major,
               v.TeamID, v.Role, v.Batch,
               v.AssignedCountyCode AS CountyCode,
               v.AssignedCountyName AS CountyName,
               v.AssignedProvince AS Province,
               v.CompletedInterviews, v.PendingInterviews,
               v.ActualInterviewCount, v.AvgInterviewQuality,
               v.LatestInterviewDate, v.CoveredCounties,
               s.Expertise, s.Notes
        FROM v_surveyor_work_statistics v
        LEFT JOIN surveyors s ON v.SurveyorID = s.SurveyorID
        WHERE 1=1
    """
    params = []

    if keyword:
        sql += " AND (v.Name LIKE %s OR v.SurveyorID LIKE %s)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    if county_code:
        sql += " AND v.AssignedCountyCode = %s"
        params.append(county_code)

    sql += " ORDER BY v.ActualInterviewCount DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        result = execute_query(sql, params)
        
        # 视图不包含Phone和Email，需要额外JOIN surveyors表获取敏感字段
        user_role = session.get('role')
        is_privileged = user_role in ['admin', 'analyst', 'surveyor']
        
        # 如果需要联系方式，额外查询并合并
        if result and is_privileged:
            surveyor_ids = [row['SurveyorID'] for row in result]
            if surveyor_ids:
                placeholders = ','.join(['%s'] * len(surveyor_ids))
                contact_sql = f"""
                    SELECT SurveyorID, Phone, Email
                    FROM surveyors
                    WHERE SurveyorID IN ({placeholders})
                """
                contact_result = execute_query(contact_sql, surveyor_ids)
                # 创建映射
                contact_map = {row['SurveyorID']: row for row in contact_result}
                # 合并到结果中
                for row in result:
                    surveyor_id = row['SurveyorID']
                    if surveyor_id in contact_map:
                        row['Phone'] = contact_map[surveyor_id].get('Phone')
                        row['Email'] = contact_map[surveyor_id].get('Email')
        
        # 获取总数
        count_sql = """
            SELECT COUNT(*) as total 
            FROM v_surveyor_work_statistics v
            WHERE 1=1
        """
        count_params = []
        
        if keyword:
            count_sql += " AND (v.Name LIKE %s OR v.SurveyorID LIKE %s)"
            count_params.extend([f'%{keyword}%', f'%{keyword}%'])
        if county_code:
            count_sql += " AND v.AssignedCountyCode = %s"
            count_params.append(county_code)
            
        total_res = execute_query(count_sql, count_params)
        total = total_res[0]['total'] if total_res else 0

        return jsonify({
            'success': True,
            'data': result,
            'total': total,
            'note': 'Using view: v_surveyor_work_statistics'
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


@bp.route('/<surveyor_id>/performance', methods=['GET'])
def get_surveyor_performance(surveyor_id):
    """获取调研员工作绩效分析（使用存储过程）"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 调用存储过程
        cursor.callproc('sp_get_surveyor_performance', (surveyor_id,))
        result = cursor.fetchall()
        
        if result:
            return jsonify({
                'success': True,
                'data': result[0] if len(result) == 1 else result,
                'note': 'Using stored procedure: sp_get_surveyor_performance'
            })
        else:
            return jsonify({'success': False, 'error': '调研员不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

