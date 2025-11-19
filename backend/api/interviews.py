"""
访谈记录API
"""
from flask import Blueprint, jsonify, request
from backend.db import execute_query

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


@bp.route('/words', methods=['GET'])
def get_word_cloud():
    """获取词云数据"""
    import jieba
    from collections import Counter
    
    county_code = request.args.get('county_code')
    limit = request.args.get('limit', type=int, default=100)
    
    sql = "SELECT Content FROM interviews WHERE Content IS NOT NULL"
    params = []
    
    if county_code:
        sql += " AND CountyCode = %s"
        params.append(county_code)
        
    try:
        rows = execute_query(sql, params)
        text = " ".join([r['Content'] for r in rows])
        
        # 停用词表
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '我们', '你们', '他们', '但是', '因为', '所以', '如果', '其实', '就是', '还是', '只是', '比如', '或者', '然后', '那个', '这个', '一些', '一种', '一样', '一直', '一定', '一般', '可能', '觉得', '感觉', '知道', '看到', '出来', '出来', '现在', '以前', '后来', '时候', '地方', '东西', '事情', '问题', '情况', '方面', '办法', '方法', '方式', '过程', '结果', '效果', '原因', '影响', '意义', '价值', '作用', '目的', '目标', '任务', '工作', '生活', '学习', '发展', '建设', '建设', '扶贫', '脱贫', '贫困', '困难', '帮助', '支持', '政策', '项目', '资金', '资金', '产业', '产业', '就业', '教育', '医疗', '住房', '保障', '保障', '服务', '服务', '管理', '管理', '组织', '组织', '实施', '实施', '开展', '开展', '进行', '进行', '推进', '推进', '落实', '落实', '完成', '完成', '实现', '实现', '取得', '取得', '达到', '达到', '提高', '提高', '改善', '改善', '增强', '增强', '加强', '加强', '促进', '促进', '推动', '推动', '加大', '加大', '增加', '增加', '减少', '减少', '降低', '降低', '解决', '解决'
        }
        # 添加一些业务相关的常用词到停用词表，避免它们占据太大比例
        stopwords.update(['县', '乡', '村', '户', '贫困户', '书记', '干部', '工作队', '驻村', '第一'])

        words = jieba.cut(text)
        filtered_words = [w for w in words if len(w) > 1 and w not in stopwords]
        
        word_counts = Counter(filtered_words)
        result = [{'name': k, 'value': v} for k, v in word_counts.most_common(limit)]
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

