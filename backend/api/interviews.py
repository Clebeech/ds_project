"""
访谈记录API
"""
from flask import Blueprint, jsonify, request, session
from backend.db import execute_query
from backend.api.auth import login_required, admin_required
import jieba
import re
from collections import Counter

bp = Blueprint('interviews', __name__, url_prefix='/api/interviews')

import datetime
import uuid

# 中文停用词列表（简化版）
STOP_WORDS = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}

# ... existing imports ...

@bp.route('', methods=['POST'])
@login_required
def create_interview():
    """创建访谈记录 (Admin or Surveyor)"""
    if session.get('role') not in ['admin', 'surveyor']:
         return jsonify({'success': False, 'error': 'Forbidden: Permission denied', 'code': 403}), 403
         
    data = request.get_json()
    
    # 必填字段
    required_fields = ['surveyor_id', 'county_code', 'content']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
            
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Generate ID
        interview_id = f"I{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Insert
        sql = """
            INSERT INTO interviews (
                InterviewID, SurveyorID, CountyCode, IntervieweeID,
                IntervieweeName, IntervieweeInfo, Content, InterviewDate,
                InterviewLocation, Quality
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            interview_id,
            data['surveyor_id'],
            data['county_code'],
            data.get('interviewee_id'),
            data.get('interviewee_name'),
            data.get('interviewee_info'),
            data['content'],
            data.get('date') or datetime.date.today(),
            data.get('location'),
            data.get('quality', 5.0)
        ))
        
        conn.commit()
        
        return jsonify({'success': True, 'interview_id': interview_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

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


@bp.route('/wordcloud', methods=['GET'])
def get_wordcloud():
    """获取访谈词云数据"""
    county_code = request.args.get('county_code')
    surveyor_id = request.args.get('surveyor_id')
    limit = request.args.get('limit', type=int, default=50)
    
    # 构建查询条件
    sql = "SELECT Content FROM interviews WHERE Content IS NOT NULL AND Content != ''"
    params = []
    
    if county_code:
        sql += " AND CountyCode = %s"
        params.append(county_code)
    if surveyor_id:
        sql += " AND SurveyorID = %s"
        params.append(surveyor_id)
    
    try:
        result = execute_query(sql, params)
        
        # 合并所有访谈内容
        all_text = ' '.join([row.get('Content', '') or '' for row in result])
        
        if not all_text:
            return jsonify({'success': True, 'data': []})
        
        # 使用jieba分词
        words = jieba.cut(all_text)
        
        # 过滤：只保留长度>=2的中文词，排除停用词和纯数字
        filtered_words = []
        for word in words:
            word = word.strip()
            if (len(word) >= 2 and 
                re.match(r'^[\u4e00-\u9fa5]+$', word) and  # 只保留中文
                word not in STOP_WORDS):
                filtered_words.append(word)
        
        # 统计词频
        word_freq = Counter(filtered_words)
        
        # 转换为词云格式 [{name: '词', value: 频次}]
        wordcloud_data = [
            {'name': word, 'value': count}
            for word, count in word_freq.most_common(limit)
        ]
        
        return jsonify({'success': True, 'data': wordcloud_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

