"""
832工程数据库应用系统 - Flask主应用
"""
from flask import Flask
from flask_cors import CORS
from backend.api import counties, interviews, compare, stats, auth, surveyors

app = Flask(__name__)
app.secret_key = 'dev_secret_key_832_project'  # 开发环境密钥，生产环境应使用环境变量
CORS(app, supports_credentials=True)  # 允许跨域携带 Cookie

# 注册蓝图
app.register_blueprint(counties.bp)
app.register_blueprint(interviews.bp)
app.register_blueprint(compare.bp)
app.register_blueprint(stats.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(surveyors.bp)


@app.route('/')
def index():
    """根路径"""
    return {
        'name': '832工程数据库应用系统',
        'version': '1.0.0',
        'description': '为政府扶贫政策分析师提供脱贫案例库支持',
        'endpoints': {
            'counties': '/api/counties',
            'interviews': '/api/interviews',
            'compare': '/api/compare',
            'stats': '/api/stats'
        }
    }


@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'error': '接口不存在'}, 404


@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'error': '服务器内部错误'}, 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
else:
    # 用于生产环境部署
    application = app

