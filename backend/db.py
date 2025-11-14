"""
数据库连接模块
"""
import pymysql
from functools import wraps

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'poverty_alleviation_832',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def db_query(func):
    """数据库查询装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    return wrapper


def execute_query(sql, params=None):
    """执行查询并返回结果"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()
        conn.close()

