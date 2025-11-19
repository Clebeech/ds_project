-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    role ENUM('admin', 'analyst', 'guest') NOT NULL DEFAULT 'guest' COMMENT '角色',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_login TIMESTAMP NULL COMMENT '最后登录时间'
) COMMENT='系统用户表' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建访问日志表
CREATE TABLE IF NOT EXISTS access_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '关联用户ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型：LOGIN, LOGOUT, VIEW_SENSITIVE',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) COMMENT='用户访问日志' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

