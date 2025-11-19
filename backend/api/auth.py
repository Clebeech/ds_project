from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from backend.db import get_db_connection, execute_query
import functools
import datetime

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized', 'code': 401}), 401
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized', 'code': 401}), 401
        if session.get('role') != 'admin':
             return jsonify({'success': False, 'error': 'Forbidden: Admin access required', 'code': 403}), 403
        return view(**kwargs)
    return wrapped_view

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码不能为空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Log access
            cursor.execute(
                "INSERT INTO access_logs (user_id, action, ip_address) VALUES (%s, %s, %s)",
                (user['user_id'], 'LOGIN', request.remote_addr)
            )
            conn.commit()

            return jsonify({
                'success': True,
                'user': {
                    'id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
            })
        
        return jsonify({'success': False, 'error': '用户名或密码错误'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@bp.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO access_logs (user_id, action, ip_address) VALUES (%s, %s, %s)",
                (user_id, 'LOGOUT', request.remote_addr)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass

    session.clear()
    return jsonify({'success': True})

@bp.route('/me', methods=['GET'])
def me():
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        })
    return jsonify({'success': False, 'user': None})

