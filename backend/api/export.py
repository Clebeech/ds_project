"""
数据导出API
支持导出CSV格式的数据
"""
import csv
import io
from flask import Blueprint, jsonify, request, Response
from backend.db import execute_query
from backend.api.auth import login_required, admin_required

bp = Blueprint('export', __name__, url_prefix='/api/export')


@bp.route('/counties', methods=['GET'])
@login_required
def export_counties():
    """导出县域数据为CSV"""
    try:
        # 获取筛选条件
        region = request.args.get('region')
        exit_year = request.args.get('exit_year')
        
        sql = """
            SELECT CountyCode, CountyName, Province, City,
                   Longitude, Latitude, ExitYear, Region,
                   GDP, PerCapitaGDP, RuralDisposableIncome
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
        
        result = execute_query(sql, params)
        
        if not result:
            return jsonify({'success': False, 'error': '没有数据可导出'}), 404
        
        # 创建CSV
        output = io.StringIO()
        if result:
            fieldnames = list(result[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result)
        
        # 返回CSV文件
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=counties.csv'}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/interviews', methods=['GET'])
@login_required
def export_interviews():
    """导出访谈记录为CSV"""
    try:
        # 获取筛选条件
        county_code = request.args.get('county_code')
        surveyor_id = request.args.get('surveyor_id')
        
        sql = """
            SELECT i.InterviewID, i.InterviewDate, i.InterviewLocation,
                   i.InterviewType, i.Quality, i.Summary,
                   c.CountyName, s.Name as SurveyorName
            FROM interviews i
            LEFT JOIN county c ON i.CountyCode = c.CountyCode
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
        
        sql += " ORDER BY i.InterviewDate DESC"
        
        result = execute_query(sql, params)
        
        if not result:
            return jsonify({'success': False, 'error': '没有数据可导出'}), 404
        
        # 创建CSV（不包含Content字段，太长）
        output = io.StringIO()
        if result:
            # 移除Content字段
            fieldnames = [k for k in result[0].keys() if k != 'Content']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in result:
                row_clean = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(row_clean)
        
        # 返回CSV文件
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=interviews.csv'}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/surveyors', methods=['GET'])
@login_required
def export_surveyors():
    """导出调研员数据为CSV"""
    try:
        sql = """
            SELECT v.SurveyorID, v.Name, v.Department, v.Education, v.Major,
                   v.TeamID, v.Role, v.CountyCode, v.CountyName,
                   v.CompletedInterviews, v.ActualInterviewCount,
                   v.AvgInterviewQuality
            FROM v_surveyor_work_statistics v
            ORDER BY v.ActualInterviewCount DESC
        """
        
        result = execute_query(sql)
        
        if not result:
            return jsonify({'success': False, 'error': '没有数据可导出'}), 404
        
        # 创建CSV
        output = io.StringIO()
        if result:
            fieldnames = list(result[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(result)
        
        # 返回CSV文件
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=surveyors.csv'}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

