"""
统计数据API
"""
from flask import Blueprint, jsonify
from backend.db import execute_query

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

