-- 修改 role 列定义，增加 'surveyor'
ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'analyst', 'surveyor', 'guest') NOT NULL DEFAULT 'guest';

